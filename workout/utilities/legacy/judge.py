"""
Main application for movement detection and counting
Integrates movement classification with movement-specific rep counting
"""
import cv2
import PoseModule as pm
from workout.utilities.utils import load_movement_criteria
from movement_classifier import MovementClassifier
from movement_counters import SquatCounter, PushUpCounter, PullUpCounter, ToesToBarCounter


class Judge:
    """Main application class for judging functional movements"""

    def __init__(self, video_source, criteria):
        """
        Initialize the Judge

        Args:
            video_source: Path to video file or camera index (0 for webcam)
            criteria: Dictionary of movement criteria from JSON config
        """
        self.video = cv2.VideoCapture(video_source)
        self.criteria = criteria
        self.detector = pm.PoseDetector()

        # Initialize classifier
        self.classifier = MovementClassifier(buffer_size=15)

        # Initialize all counters
        self.counters = {
            'squat': SquatCounter(criteria.get('squat', {})),
            'push_up': PushUpCounter(criteria.get('push_up', {})),
            'pull_up': PullUpCounter(criteria.get('pull_up', {})),
            'toes_to_bar': ToesToBarCounter(criteria.get('toes_to_bar', {}))
        }

        self.current_movement = None
        self.current_counter = None
        self.paused = False

    def get_angle_for_movement(self, movement_type, lmList):
        """
        Get the appropriate angle measurement for the detected movement

        Args:
            movement_type: Type of movement detected
            lmList: List of pose landmarks

        Returns:
            tuple: (angle, hip_index, knee_index, ankle_index) or (angle, p1, p2, p3)
        """
        if movement_type == 'squat':
            # For squats, use hip-knee-ankle angle
            hip_index, knee_index, ankle_index = self.detector.getLandmarkIndices(
                lmList, is_squat=True
            )
            angle = self.detector.getAngle(
                None, hip_index, knee_index, ankle_index
            )
            return angle, hip_index, knee_index, ankle_index

        elif movement_type == 'push_up':
            # For push-ups, use shoulder-elbow-wrist angle
            # Use right side (can average both sides for more stability)
            shoulder_idx = 12  # right shoulder
            elbow_idx = 14  # right elbow
            wrist_idx = 16  # right wrist
            angle = self.detector.getAngle(
                None, shoulder_idx, elbow_idx, wrist_idx
            )
            return angle, shoulder_idx, elbow_idx, wrist_idx

        elif movement_type == 'pull_up':
            # For pull-ups, use shoulder-elbow angle or elbow angle
            shoulder_idx = 12  # right shoulder
            elbow_idx = 14  # right elbow
            wrist_idx = 16  # right wrist
            angle = self.detector.getAngle(
                None, shoulder_idx, elbow_idx, wrist_idx
            )
            return angle, shoulder_idx, elbow_idx, wrist_idx

        elif movement_type == 'toes_to_bar':
            # For T2B, use hip-knee-ankle or hip angle
            hip_idx = 24  # right hip
            knee_idx = 26  # right knee
            ankle_idx = 28  # right ankle
            angle = self.detector.getAngle(
                None, hip_idx, knee_idx, ankle_idx
            )
            return angle, hip_idx, knee_idx, ankle_idx

        return None, None, None, None

    def process_frame(self, img, lmList):
        """
        Process a single frame: classify movement and count reps

        Args:
            img: Current frame image
            lmList: Pose landmarks for current frame

        Returns:
            dict: Stats for current frame
        """
        stats = {
            'movement': None,
            'count': 0,
            'no_rep': 0,
            'outcome': '',
            'angle': 0
        }

        if len(lmList) == 0:
            return stats

        # Classify the movement
        detected_movement = self.classifier.classify(lmList, self.detector)

        # Check if movement changed
        if detected_movement != self.current_movement and detected_movement is not None:
            print(f"\n{'=' * 50}")
            print(f"Movement changed: {self.current_movement} -> {detected_movement}")
            print(f"{'=' * 50}\n")
            self.current_movement = detected_movement
            self.current_counter = self.counters.get(detected_movement)

            # Reset counter when switching movements
            if self.current_counter:
                self.current_counter.reset()

        stats['movement'] = self.current_movement

        # If we have a recognized movement, process counting
        if self.current_movement and self.current_counter:
            # Get the appropriate angle for this movement
            angle, p1, p2, p3 = self.get_angle_for_movement(
                self.current_movement, lmList
            )

            if angle is not None:
                # Get movement-specific criteria
                movement_criteria = self.criteria.get(self.current_movement, {})
                descending_threshold = movement_criteria.get('descending_threshold', 110)
                ascending_threshold = movement_criteria.get('ascending_threshold', 110)

                # Determine direction
                direction = self.detector.checkDirectionFromAngle(
                    angle,
                    descending_threshold,
                    ascending_threshold,
                    self.current_counter.previous_angle,
                    downward_movement=(self.current_movement in ['squat', 'push_up'])
                )

                # Process the rep
                counter_stats = self.current_counter.process(
                    angle, lmList, self.detector, direction
                )

                # Update stats
                stats.update(counter_stats)
                stats['angle'] = angle

        return stats

    def draw_ui(self, img, stats):
        """
        Draw UI elements on the frame

        Args:
            img: Frame image
            stats: Current statistics
        """
        # Movement type
        movement_text = stats['movement'] if stats['movement'] else 'Detecting...'
        cv2.putText(
            img, f'Movement: {movement_text}',
            (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 0), 3
        )

        # Rep counts
        cv2.putText(
            img, f'Good Reps: {stats["count"]}',
            (50, 100), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 5
        )

        cv2.putText(
            img, f'No Reps: {stats["no_rep"]}',
            (500, 100), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 5
        )

        # Outcome
        if stats['outcome']:
            outcome_color = (0, 255, 0) if stats['outcome'] == 'good rep' else (0, 165, 255)
            cv2.putText(
                img, f'Outcome: {stats["outcome"]}',
                (50, 200), cv2.FONT_HERSHEY_PLAIN, 2, outcome_color, 3
            )

        # Current angle (for debugging)
        if stats['angle'] > 0:
            cv2.putText(
                img, f'Angle: {int(stats["angle"])}',
                (50, 250), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2
            )

        # Instructions
        cv2.putText(
            img, 'SPACE: Pause | Q/ESC: Quit',
            (50, img.shape[0] - 30), cv2.FONT_HERSHEY_PLAIN, 1.5, (200, 200, 200), 2
        )

    def run(self):
        """Main application loop"""
        print("Judge started!")
        print("Controls:")
        print("  SPACE - Pause/Resume")
        print("  Q or ESC - Quit")
        print("\nDetecting movement...\n")

        while True:
            if not self.paused:
                success, img = self.video.read()

                if not success:
                    print("End of video or camera error")
                    break

                # Get pose
                img = self.detector.getPose(img, draw=True)
                lmList = self.detector.getPosition(img, draw=False)

                # Process frame
                stats = self.process_frame(img, lmList)

                # Draw UI
                self.draw_ui(img, stats)

                # Show frame
                cv2.imshow("Judge", img)
            else:
                # If paused, just show the last frame
                cv2.imshow("Judge", img)

            # Handle keyboard input
            key = cv2.waitKey(1)
            if key == 32:  # Space bar
                self.paused = not self.paused
                status = "PAUSED" if self.paused else "RESUMED"
                print(f"\n{status}\n")

            elif key == ord('q') or key == 27:  # Q or ESC
                break

        # Cleanup
        self.video.release()
        cv2.destroyAllWindows()

        # Print final stats
        print("\n" + "=" * 50)
        print("Final Statistics:")
        print("=" * 50)
        for movement, counter in self.counters.items():
            stats = counter.get_stats()
            if stats['count'] > 0 or stats['no_rep'] > 0:
                print(f"\n{movement.upper()}:")
                print(f"  Good Reps: {stats['count']}")
                print(f"  No Reps: {stats['no_rep']}")


def main():
    """Main entry point"""
    # Load movement criteria
    criteria = load_movement_criteria()

    # Video source - change this to test different videos
    # video_source = 0  # Webcam
    video_source = '../static/videos/airsquat.mp4'  # Video file

    # Create and run judge
    judge = Judge(video_source, criteria)
    judge.run()


if __name__ == "__main__":
    main()
