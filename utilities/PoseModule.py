import cv2
import mediapipe as mp
import time
import math
import threading
import queue

import numpy as np


class PoseProcessor:
    def __init__(self, detector):
        super().__init__()
        self.detector = detector
        self.frame_queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.running = False
        self.lock = threading.Lock()
        self.processing_thread = threading.Thread(
            target=self.process_frame,
        )

    def start(self):
        self.running = True
        self.processing_thread.start()

    def process_frame(self):
        # initial variables
        count = 0
        no_rep = 0
        # 1 = up, 0 = down
        direction = None
        start_point = 170
        end_point = 10
        is_movement_started = False
        full_range = False
        full_extension = False
        outcome = ""
        descending_threshold = 30  # Threshold to indicate start of squat
        ascending_threshold = 150
        full_range_threshold = 250  # Adjust threshold based on your requirement
        previous_angle = 0

        while self.running:
            frame = self.frame_queue.get()
            if frame is None:  # Signal to stop processing
                break

            # Pose detection and processing
            processed_frame = self.detector.getPose(frame)
            lmList = self.detector.getPosition(processed_frame, draw=False)

            if len(lmList) != 0:
                # landmarks for hands and feet to check for full range
                left_hand_y = min(lmList[19][2], lmList[17][2])
                right_hand_y = min(lmList[20][2], lmList[18][2])
                left_toe_y = lmList[31][2]
                right_toe_y = lmList[32][2]

                # # Pose detection and processing
                # frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                # results = pose.process(frame_rgb)
                #
                # # Extract the relevant joint positions from the lmList
                # right_hip_x = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP].x
                # right_hip_y = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_HIP].y
                # right_knee_x = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE].x
                # right_knee_y = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_KNEE].y
                # right_ankle_x = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE].x
                # right_ankle_y = results.pose_landmarks.landmark[mp_pose.PoseLandmark.RIGHT_ANKLE].y
                # left_hip_x = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].x
                # left_hip_y = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_HIP].y
                # left_knee_x = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE].x
                # left_knee_y = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_KNEE].y
                # left_ankle_x = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].x
                # left_ankle_y = results.pose_landmarks.landmark[mp_pose.PoseLandmark.LEFT_ANKLE].y

                # get visibility depending on which way athlete is facing
                left_hip_visibility = lmList[23][3]  # Visibility of left hip (landmark 23)
                right_hip_visibility = lmList[24][3]  # Visibility of right hip (landmark 24)

                # Choose landmarks based on hip visibility
                if left_hip_visibility > right_hip_visibility:
                    # Use left side landmarks
                    shoulder_index = 11
                    hip_index = 23
                    ankle_index = 27
                else:
                    # Use right side landmarks
                    shoulder_index = 12
                    hip_index = 24
                    ankle_index = 28

                # Calculate the angle
                # Need to use the angle to check for start, end of rep and rep started
                angle = self.detector.getAngle(processed_frame, shoulder_index, hip_index, ankle_index)

                percentage = int(round(np.interp(angle, (end_point, start_point), (100, 0))))

                # imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                # results = pose.process(imgRGB)
                # landmarks = results.pose_landmarks.landmark

                # # Get coordinates for toes (Landmarks 31 and 32)
                # left_toe = [landmarks[31].x, landmarks[31].y]
                # right_toe = [landmarks[32].x, landmarks[32].y]
                # right_hand = [landmarks[20].x, landmarks[20].y]
                # left_hand = [landmarks[19].x, landmarks[19].y]
                # # Convert coordinates to pixel values
                # h, w, c = img.shape
                # left_toe_pixel = np.multiply(left_toe, [w, h]).astype(int)
                # right_toe_pixel = np.multiply(right_toe, [w, h]).astype(int)
                # left_hand_pixel = np.multiply(left_hand, [w, h]).astype(int)
                # right_hand_pixel = np.multiply(right_hand, [w, h]).astype(int)
                # # Draw circles at the toe positions
                # cv2.circle(img, tuple(left_toe_pixel), 15, (255, 0, 0), -1)  # Blue circle for left toe
                # cv2.circle(img, tuple(right_toe_pixel), 15, (0, 255, 0), -1)  # Green circle
                # cv2.circle(img, tuple(left_hand_pixel), 15, (255, 0, 0), -1)  # Blue circle for left hand
                # cv2.circle(img, tuple(right_hand_pixel), 15, (0, 255, 0), -1)

                # Movement analysis logic
                if angle > ascending_threshold:
                    direction = 1  # Up
                elif angle < descending_threshold:
                    direction = 0  # Down

                # Movement analysis logic
                if direction == 1 and angle < ascending_threshold:
                    if not is_movement_started:
                        is_movement_started = True
                        full_range = False
                        full_extension = False
                        outcome = ''

                if angle <= 10:
                    full_range = True

                    # METHOD TO USE Y COORDINATES FOR RANGE
                    # if abs(left_hand_y - left_toe_y) < full_range_threshold or abs(
                    #         right_hand_y - right_toe_y) < full_range_threshold:
                    #     full_range = True

                    # print("left", left_hand_y, left_toe_y)
                    # print("right", right_hand_y, right_toe_y)

                elif direction == 1 and is_movement_started:
                    if angle >= start_point:
                        full_extension = True

                    # Check for no full extension
                    # if angle is going higher it means athlete is going up
                    if full_range:
                        if not full_extension:
                            if angle < previous_angle:
                                no_rep += 1
                                outcome = "no full extension"
                                direction = 1
                                is_movement_started = False
                    elif not full_range:
                        # if didn't reach full range and they start going down
                        if angle > previous_angle and full_extension:
                            no_rep += 1
                            outcome = "did not touch the bar"
                            direction = 0
                            is_movement_started = False

                    # # Reset variables for next rep
                    is_movement_started = False
                    full_range = False
                    full_extension = False

                if full_range and full_extension:
                    count += 1
                    outcome = "good rep"
                    # Reset variables for next rep
                    is_movement_started = False
                    full_range = False
                    full_extension = False

                # # change to int in case there are minor differences in float values
                previous_angle = int(angle)

                # Output for debugging
                print(
                    int(angle),
                    is_movement_started,
                    direction,
                    outcome,
                    "extension", full_extension,
                    "full range", full_range,
                    "reps", count,
                    "no reps", no_rep
                )
            print("Processing frame:", lmList)

            self.result_queue.put((processed_frame, count, no_rep, outcome))

    def stop(self):
        self.running = False
        while not self.frame_queue.empty():
            time.sleep(0.1)
        self.frame_queue.put(None)
        self.processing_thread.join()

    def put_frame(self, frame):
        self.frame_queue.put(frame)

    def get_result(self):
        if not self.result_queue.empty():
            return self.result_queue.get()

    def join(self):
        self.processing_thread.join()


class PoseDetector:

    def __init__(self, mode=False, model_complexity=1,
                 smooth_landmarks=True,
                 enable_segmentation=False,
                 smooth_segmentation=True,
                 detectionConfidence=0.5,
                 trackingConfidence=0.5):

        self.mode = mode
        self.model_complexity = model_complexity
        self.smooth_landmarks = smooth_landmarks
        self.enable_segmentation = enable_segmentation
        self.smooth_segmentation = smooth_segmentation
        self.detectionConfidence = detectionConfidence
        self.trackingConfidence = trackingConfidence

        self.mpPose = mp.solutions.pose
        self.mpDraw = mp.solutions.drawing_utils
        self.pose = self.mpPose.Pose(self.mode, self.model_complexity,
                                     self.smooth_landmarks, self.enable_segmentation,
                                     self.smooth_segmentation, self.detectionConfidence,
                                     self.trackingConfidence)

    def getPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        self.results = self.pose.process(imgRGB)
        # print(results.pose_landmarks)

        if self.results.pose_landmarks and draw:
            self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)

        return img

    def getPosition(self, img, draw=True):
        self.lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                cz = lm.z  # Depth value
                visibility = lm.visibility
                self.lmList.append([id, cx, cy, visibility])
                if draw:
                    cv2.circle(img, (cx, cy), 3, (255, 0, 0), cv2.FILLED)
        return self.lmList

    def getAngle(self, img, p1, p2, p3, draw=True):
        # Get the points
        x1, y1 = self.lmList[p1][1], self.lmList[p1][2]
        x2, y2 = self.lmList[p2][1], self.lmList[p2][2]
        x3, y3 = self.lmList[p3][1], self.lmList[p3][2]

        # Calculate vectors
        v1 = (x1 - x2, y1 - y2)
        v2 = (x3 - x2, y3 - y2)

        # Calculate dot product and magnitude of vectors
        dot = v1[0] * v2[0] + v1[1] * v2[1]
        mag1 = math.sqrt(v1[0] ** 2 + v1[1] ** 2)
        mag2 = math.sqrt(v2[0] ** 2 + v2[1] ** 2)

        if mag1 * mag2 == 0:
            return 0

            # Clamp value between -1 and 1
        cosine_angle = max(min(dot / (mag1 * mag2), 1), -1)

        # Calculate the angle in radians and then convert to degrees
        angle = math.degrees(math.acos(cosine_angle))

        if draw:
            # draws white line from points for visibility
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
            # creates a target shape for the point
            cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x1, y1), 15, (0, 0, 255), 2)
            cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (0, 0, 255), 2)
            cv2.circle(img, (x3, y3), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x3, y3), 15, (0, 0, 255), 2)
            cv2.putText(
                img,
                str(int(angle)),
                (x2 + 50, y2),
                cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 4
            )
        return angle

    def getLandmarks(self):
        if self.results.pose_landmarks:
            return self.results.pose_landmarks.landmark
        return None

    def checkDirection(self, angle, descending_threshold, ascending_threshold, previous_angle, downward_movement):
        """
                Determines the direction of movement based on the given angle and thresholds.

                Parameters:
                angle (float): The current angle to be evaluated.
                descending_threshold (float): The threshold angle for descending movement.
                ascending_threshold (float): The threshold angle for ascending movement.

                Returns:
                string: '1' if ascending, '0' if descending, or None if the direction is not determined.
                """
        buffer_zone = 5
        if downward_movement:
            if angle > ascending_threshold - buffer_zone:
                return 1  # Ascending
            elif angle < descending_threshold + buffer_zone:
                return 0  # Descending
            else:
                # Check the trend when in the buffer zone
                if previous_angle is not None:
                    if angle > previous_angle:
                        return 1  # Ascending
                    elif angle < previous_angle:
                        return 0  # Descending

                return None  # Direction not determined
        else:
            if angle < ascending_threshold - buffer_zone:
                return 1  # Ascending
            elif angle > descending_threshold + buffer_zone:
                return 0  # Descending
            else:
                # Check the trend when in the buffer zone
                if previous_angle is not None:
                    if angle < previous_angle:
                        return 1  # Ascending
                    elif angle > previous_angle:
                        return 0  # Descending

                return None  # Direction not determined

    def getLandmarkIndices(self, lmList, is_squat=False, is_arm_extension=False):
        """
        Determines the correct landmarks based on athlete's visibility and orientation.

        Parameters:
        lmList (list): List containing landmarks with their visibility scores.

        Returns:
        tuple: Indices for shoulder, hip, and ankle landmarks.
        """

        left_hip_visibility = lmList[23][3]  # Visibility of left hip (landmark 23)
        right_hip_visibility = lmList[24][3]  # Visibility of right hip (landmark 24)
        if is_squat:
            if left_hip_visibility > right_hip_visibility:
                # Use left side landmarks (23, 25, 27)
                return 23, 25, 27
            else:
                return 24, 26, 28
        elif is_arm_extension:
            if left_hip_visibility > right_hip_visibility:
                return 11, 13, 15  # shoulder, hip, ankle indices
            else:
                # Use right side landmarks
                return 12, 14, 16  # shoulder, hip, ankle indices
        else:
            if left_hip_visibility > right_hip_visibility:
                # Use left side landmarks
                return 11, 23, 27  # shoulder, hip, ankle indices
            else:
                # Use right side landmarks
                return 12, 24, 28  # shoulder, hip, ankle indices

    def checkPullUpFullRange(self, left_hand_threshold_check,  right_hand_threshold_check, full_range_threshold):

        if left_hand_threshold_check < full_range_threshold or right_hand_threshold_check < full_range_threshold:
            full_range = True
            return full_range


# def process_frame(detector, frame_queue, result_queue):
#     while True:
#         frame = frame_queue.get()
#         if frame is None:  # Signal to stop processing
#             break
#
#         # Pose detection and processing
#         processed_frame = detector.getPose(frame)
#         lmList = detector.getPosition(processed_frame, draw=False)
#         # ... (additional processing logic)
#
#         # Put the processed frame (and any other data) in the result queue
#         result_queue.put((processed_frame, lmList))
#
#
# def stop_threads(frame_queue, processing_thread):
#     frame_queue.put(None)
#     processing_thread.join()


# def main():
#     video = cv2.VideoCapture('../videos/toestobar.MOV')
#     detector = PoseDetector()
#     pose_processor = PoseProcessor(detector)
#     pose_processor.start()
#     pTime = 0
#
#     try:
#         while True:
#             success, img = video.read()
#             if not success:
#                 break
#
#             pose_processor.put_frame(img)
#             result = pose_processor.get_result()
#             display_frame = img
#
#             if result:
#                 processed_frame, lmList = result
#                 display_frame = processed_frame
#                 # Display the processed frame or use lmList for further logic
#
#             cTime = time.time()
#             fps = 1 / (cTime - pTime) if pTime != 0 else 0
#             pTime = cTime
#             cv2.putText(display_frame, f'FPS: {int(fps)}', (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
#
#             # Display the frame
#             cv2.imshow("Video", display_frame)
#
#             # Handle the exit condition
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
#
#     finally:
#         pose_processor.stop()
#         pose_processor.join()
#
#         video.release()
#         cv2.destroyAllWindows()
#
#
# if __name__ == '__main__':
#     main()

# def main():
#     video = cv2.VideoCapture('../videos/toestobar.MOV')
#     pTime = 0
#     detector = PoseDetector()
#
#     frame_queue = queue.Queue()
#     result_queue = queue.Queue()
#     processing_thread = threading.Thread(target=process_frame, args=(detector, frame_queue, result_queue))
#     processing_thread.start()
#
#     try:
#         while True:
#             success, img = video.read()
#             if not success:
#                 break
#
#             frame_queue.put(img)
#             processed_frame = img
#
#             if not result_queue.empty():
#                 processed_frame, lmList = result_queue.get()
#                 # Display the processed frame or use lmList for further logic
#                 print(lmList[24])
#                 cv2.circle(img, (lmList[24][1], lmList[24][2]), 15, (0, 255, 0), cv2.FILLED)
#
#             cTime = time.time()
#             fps = 1 / (cTime - pTime)
#             pTime = cTime
#             cv2.putText(processed_frame, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0,), 3)
#             cv2.imshow("recording", processed_frame)
#             if cv2.waitKey(1) & 0xFF == ord('q'):
#                 break
#     finally:
#         stop_threads(frame_queue, processing_thread)
#         video.release()
#         cv2.destroyAllWindows()

# def main():
#     video = cv2.VideoCapture('../videos/toestobar.MOV')
#     pTime = 0
#     detector = PoseDetector()
#
#     while True:
#         success, img = video.read()
#         img = detector.getPose(img)
#         lmList = detector.getPosition(img, draw=False)
#         if len(lmList) != 0:
#             print(lmList[24])
#             cv2.circle(img, (lmList[24][1], lmList[24][2]), 15, (0, 255, 0), cv2.FILLED)
#         # detector.checkSquat(img)
#         cTime = time.time()
#         fps = 1 / (cTime - pTime)
#         pTime = cTime
#
#         cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0,), 3)
#         cv2.imshow("recording", img)
#         cv2.waitKey(1)


# if __name__ == '__main__':
#     main()

