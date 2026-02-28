"""
Movement Classifier for CrossFit Movements
Uses rule-based detection on MediaPipe pose landmarks
"""
import numpy as np
from collections import deque


class MovementClassifier:
    """
    Classifies CrossFit movements based on pose landmarks
    Uses a confidence buffer to avoid flickering between movements
    """

    def __init__(self, buffer_size=15):
        """
        Args:
            buffer_size: Number of frames to buffer for stable classification
        """
        self.buffer_size = buffer_size
        self.confidence_buffer = deque(maxlen=buffer_size)
        self.current_movement = None
        self.frames_stable = 0
        self.min_stable_frames = 20  # Require 20 frames of same detection before switching

    def classify(self, lmList, detector):
        """
        Classify the current movement based on pose landmarks

        Args:
            lmList: List of pose landmarks from MediaPipe
            detector: PoseDetector instance

        Returns:
            str: Movement type ('squat', 'push_up', 'pull_up', 'toes_to_bar', None)
        """
        if len(lmList) == 0:
            return None

        # Extract features from pose
        features = self._extract_features(lmList, detector)

        # Rule-based classification
        detected_movement = self._classify_from_features(features)

        # Add to confidence buffer
        self.confidence_buffer.append(detected_movement)

        # Get most common movement in buffer
        if len(self.confidence_buffer) >= self.buffer_size:
            movement_counts = {}
            for m in self.confidence_buffer:
                if m is not None:
                    movement_counts[m] = movement_counts.get(m, 0) + 1

            if movement_counts:
                buffered_movement = max(movement_counts, key=movement_counts.get)
                confidence = movement_counts[buffered_movement] / self.buffer_size

                # Only change movement if we have high confidence
                if confidence > 0.6:
                    if buffered_movement == self.current_movement:
                        self.frames_stable += 1
                    else:
                        self.frames_stable = 0

                    # Switch movement if stable for enough frames
                    if self.frames_stable >= self.min_stable_frames or self.current_movement is None:
                        self.current_movement = buffered_movement

        return self.current_movement

    def _extract_features(self, lmList, detector):
        """
        Extract relevant features for movement classification

        Returns:
            dict: Dictionary of features
        """
        features = {}

        # Get key landmarks (using MediaPipe landmark indices)
        # 0: nose, 11: left_shoulder, 12: right_shoulder
        # 23: left_hip, 24: right_hip, 15: left_wrist, 16: right_wrist
        # 27: left_ankle, 28: right_ankle, 13: left_elbow, 14: right_elbow

        try:
            # Average left and right landmarks for stability
            shoulder_y = (lmList[11][2] + lmList[12][2]) / 2
            hip_y = (lmList[23][2] + lmList[24][2]) / 2
            wrist_y = (lmList[15][2] + lmList[16][2]) / 2
            ankle_y = (lmList[27][2] + lmList[28][2]) / 2
            nose_y = lmList[0][2]

            # X positions for horizontal analysis
            shoulder_x = (lmList[11][1] + lmList[12][1]) / 2
            hip_x = (lmList[23][1] + lmList[24][1]) / 2
            wrist_x = (lmList[15][1] + lmList[16][1]) / 2
            ankle_x = (lmList[27][1] + lmList[28][1]) / 2

            # Feature 1: Body orientation (vertical vs horizontal)
            # Calculate angle of torso relative to vertical
            torso_vector = np.array([hip_x - shoulder_x, hip_y - shoulder_y])
            vertical_vector = np.array([0, 1])

            cos_angle = np.dot(torso_vector, vertical_vector) / (
                    np.linalg.norm(torso_vector) * np.linalg.norm(vertical_vector) + 1e-6
            )
            features['body_angle'] = np.degrees(np.arccos(np.clip(cos_angle, -1, 1)))

            # Feature 2: Arms overhead (wrists above shoulders)
            features['arms_overhead'] = wrist_y < shoulder_y - 50  # 50 pixel threshold

            # Feature 3: Body horizontal alignment
            # Check if shoulder, hip, ankle are roughly aligned horizontally
            body_points_y = [shoulder_y, hip_y, ankle_y]
            features['body_horizontal'] = (max(body_points_y) - min(body_points_y)) < 100

            # Feature 4: Hands on ground (wrists near or below ankle level)
            features['hands_on_ground'] = wrist_y > ankle_y - 50

            # Feature 5: Hip-shoulder vertical distance (for squat detection)
            features['hip_shoulder_vertical_dist'] = abs(hip_y - shoulder_y)

            # Feature 6: Wrist-shoulder vertical distance (for hanging movements)
            features['wrist_shoulder_vertical_dist'] = shoulder_y - wrist_y

            # Feature 7: Head position relative to hands (for pull-ups)
            features['head_above_hands'] = nose_y < wrist_y

            # Feature 8: Leg movement range (for toes-to-bar)
            features['ankle_shoulder_dist'] = abs(ankle_y - shoulder_y)

        except (IndexError, KeyError) as e:
            # If we can't extract features, return empty dict
            print(f"Error extracting features: {e}")
            return {}

        return features

    def _classify_from_features(self, features):
        """
        Classify movement based on extracted features

        Returns:
            str or None: Movement type
        """
        if not features:
            return None

        # Classification rules (ordered by specificity)

        # 1. PUSH-UP: Body horizontal, hands on ground
        if (features.get('body_horizontal', False) and
                features.get('hands_on_ground', False) and
                features.get('body_angle', 0) > 60):
            return 'push_up'

        # 2. PULL-UP / TOES-TO-BAR: Arms overhead, hanging position
        if (features.get('arms_overhead', False) and
                features.get('wrist_shoulder_vertical_dist', 0) < -30):

            # Differentiate between pull-up and toes-to-bar
            # T2B has larger leg movement range
            ankle_shoulder = features.get('ankle_shoulder_dist', 0)

            # If ankles are near shoulders (elevated legs), likely T2B
            if ankle_shoulder < 150:  # Legs are up
                return 'toes_to_bar'
            else:
                return 'pull_up'

        # 3. SQUAT: Vertical body, hip moving vertically
        if (features.get('body_angle', 180) < 30 and  # Body relatively vertical
                not features.get('arms_overhead', False) and  # Arms not overhead
                not features.get('hands_on_ground', False)):  # Hands not on ground
            return 'squat'

        # 4. Unknown movement
        return None

    def reset(self):
        """Reset the classifier state"""
        self.confidence_buffer.clear()
        self.current_movement = None
        self.frames_stable = 0