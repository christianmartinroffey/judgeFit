import cv2
import numpy as np
import time
import math
import mediapipe as mp
import PoseModule as pm
import asyncio


# section to use a video
mpPose = mp.solutions.pose
mpDraw = mp.solutions.drawing_utils
pose = mpPose.Pose()

video = cv2.VideoCapture('../videos/toestobar.MOV')
pTime = 0

detector = pm.PoseDetector()

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

while True:
    success, img = video.read()
    img = detector.getPose(img, draw=False)

    lmList = detector.getPosition(img, draw=False)
    if len(lmList) != 0:
        # landmarks for hands and feet to check for full range
        left_hand_y = min(lmList[19][2], lmList[17][2])
        right_hand_y = min(lmList[20][2], lmList[18][2])
        left_toe_y = lmList[31][2]
        right_toe_y = lmList[32][2]

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
        angle = detector.getAngle(img, shoulder_index, hip_index, ankle_index)

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

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        print(fps)
        # Output for debugging
        # print(
        #     int(angle),
        #     is_movement_started,
        #     direction,
        #     outcome,
        #     "extension", full_extension,
        #     "full range", full_range,
        #     "reps", count,
        #     "no reps", no_rep
        # )

        cv2.putText(img, f'reps: {int(count)}', (50, 100), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 5)
        # cv2.putText(img, f'{int(percentage)} %', (50, 300), cv2.FONT_HERSHEY_PLAIN, 7, (0,0,255), 8)
        cv2.putText(img, f'no reps: {int(no_rep)}', (500, 100), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 5)
        cv2.putText(img, f'outcome: {outcome}', (50, 200), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 5)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    results = pose.process(imgRGB)


