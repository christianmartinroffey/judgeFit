import cv2
import numpy as np
import time
import math
import mediapipe as mp
import PoseModule as pm

# section to use a video
mpPose = mp.solutions.pose
mpDraw = mp.solutions.drawing_utils
pose = mpPose.Pose()

# video = cv2.VideoCapture(1)
video = cv2.VideoCapture('../videos/airsquat.mp4')
pTime = 0

detector = pm.PoseDetector()

count = 0
no_rep = 0
# 1 = up, 0 = down
direction = None
start_point = 0
end_point = 0
is_squat_started = False
full_depth = False
full_extension = False
outcome = ""
descending_threshold = 110  # Threshold to indicate start of squat
ascending_threshold = 110
previous_angle = 0

while True:
    success, img = video.read()
    img = detector.getPose(img, draw=False)

    lmList = detector.getPosition(img, draw=False)
    if len(lmList) != 0:
        left_hip_visibility = lmList[23][3]  # Visibility of left hip (landmark 23)
        right_hip_visibility = lmList[24][3]  # Visibility of right hip (landmark 24)

        # Choose landmarks based on hip visibility
        if left_hip_visibility > right_hip_visibility:
            # Use left side landmarks (23, 25, 27)
            hip_index = 23
            knee_index = 25
            ankle_index = 27
        else:
            # Use right side landmarks (24, 26, 28)
            hip_index = 24
            knee_index = 26
            ankle_index = 28

        # Calculate the angle for the squat analysis
        angle = detector.getAngle(img, hip_index, knee_index, ankle_index)
        direction = detector.checkDirection(angle, descending_threshold, ascending_threshold, previous_angle)

        # Update start and end points for the new angle range
        start_point = 170  # extended value
        end_point = 60  # full range when reached
        percentage = int(round(np.interp(angle, (end_point, start_point), (100, 0))))

        if direction == 0 and angle < descending_threshold:
            if not is_squat_started:
                is_squat_started = True
                full_depth = False
                full_extension = False
                outcome = ''

            if angle <= end_point:
                full_depth = True

        elif direction == 1 and is_squat_started:
            if angle >= start_point:
                full_extension = True

            # Check for no full extension
            # if angle is going higher it means athlete is going up
            if full_depth:
                if not full_extension:
                    if angle < previous_angle:
                        no_rep += 1
                        outcome = "no full extension"
                        direction = 0
                        is_squat_started = False
            elif not full_depth:
                # if didn't reach full depth and they start going up
                if angle > previous_angle and full_extension:
                    no_rep += 1
                    outcome = "not deep enough"
                    direction = 1
                    is_squat_started = False

            # # Reset variables for next rep
            # is_squat_started = False
            # full_depth = False
            # full_extension = False

        if full_depth and full_extension:
            count += 1
            outcome = "good rep"
            # Reset variables for next rep
            is_squat_started = False
            full_depth = False
            full_extension = False

        # change to int in case there are minor differences in float values
        previous_angle = int(angle)

        # Output for debugging or display
        print(
            int(angle),
            direction,
            outcome,
            "extension", full_extension,
            "full depth", full_depth,
            "reps", count,
            "no reps", no_rep
        )

        cv2.putText(img, f'reps: {int(count)}', (50, 100), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 5)
        # cv2.putText(img, f'{int(percentage)} %', (50, 300), cv2.FONT_HERSHEY_PLAIN, 7, (0,0,255), 8)
        cv2.putText(img, f'no reps: {int(no_rep)}', (500, 100), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 5)
        cv2.putText(img, f'outcome: {outcome}', (50, 200), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 5)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    results = pose.process(imgRGB)
