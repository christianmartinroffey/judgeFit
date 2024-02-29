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

video = cv2.VideoCapture('../static/videos/burpee2.mov')

detector = pm.PoseDetector()

count = 0
no_rep = 0
# 1 = up, 0 = down
direction = None
start_point = 170
end_point = 60
extended_body_angle = 150
is_burpee_started = False
full_extension = False  # set when athlete has jumped
full_depth = False  # this is if the pushup is complete
outcome = ""
jump_threshold = 1
pushup_depth_check = 0
upright_position_check = 0
pushup_threshold = 0.04
paused = False
average_toe_height_post_pushup = 0
vertical_distance_hands = 0


while True:
    if not paused:
        success, img = video.read()
        img = detector.getPose(img, draw=False)
        lmList = detector.getPosition(img, draw=False)

        if len(lmList) != 0:
            # Choose landmarks based on hip visibility
            # determine the best landmarks to use
            shoulder_index, hip_index, ankle_index, wrist_index, elbow_index, toe_index = detector.getLandmarkIndices(
                lmList, is_burpee=True
            )

            # Calculate the angle for the analysis
            angle = detector.getAngle(img, shoulder_index, hip_index, ankle_index)
            push_up_angle = detector.getAngle(img, shoulder_index, elbow_index, wrist_index)

            landmarks = detector.get_landmarks()

            ####### START ANALYSIS #######
            upright_position_check = detector.check_upright_position(landmarks)
            # 1. Detect descending to the ground for start of rep
            if upright_position_check < 0.3:
                is_burpee_started = True
                direction = 0

                # Calculate the average height of the toes as the new baseline
                average_toe_height_post_pushup = detector.get_current_toe_height(landmarks)

            # check for upward movement
            elif upright_position_check > 0.3:
                direction = 1

            # 2. Detect push-up phase
            if direction == 0:
                pushup_depth_check = detector.check_push_up_full_range(landmarks)
                if pushup_depth_check < pushup_threshold:
                    full_depth = True

            # 3. Detect ascending back to standing
            if direction == 1 and is_burpee_started and full_depth:
                # check body is straight first before jump or full extension
                if angle > extended_body_angle and upright_position_check > 0.2:
                    # .4 detect hands above head only when full extension is reached
                    vertical_distance_hands = detector.check_hands_above_head(landmarks)
                    # .5 detect jump phase
                    # Calculate the difference between toe starting position and current position
                    average_toe_height_current = detector.get_current_toe_height(landmarks)

                    # Check for a jump by comparing the current toe height to the new baseline
                    # if these checks pass then it's a good rep so set full_extension to True
                    if average_toe_height_post_pushup > average_toe_height_current and vertical_distance_hands > 0.1:
                        full_extension = True

            elif direction == 1 and is_burpee_started and not full_depth:
                # check if they reach full extension but didn't do the push up
                vertical_distance_hands = detector.check_hands_above_head(landmarks)
                average_toe_height_current = detector.get_current_toe_height(landmarks)

                if average_toe_height_post_pushup > average_toe_height_current and vertical_distance_hands > 0.1:
                    full_extension = True
                    no_rep += 1
                    outcome = "not deep enough"
                    is_burpee_started = False
                    full_depth = False

            # if checks are passed then it's a good rep
            if full_depth and full_extension:
                count += 1
                outcome = "good rep"
                # Reset variables for next rep
                is_burpee_started = False
                full_depth = False
                full_extension = False

            # change to int in case there are minor differences in float values
            previous_angle = int(angle)

            # Output for debugging or display
            print(
                # int(angle),
                direction,
                # outcome,
                # "burpee started", is_burpee_started,
                # "full depth", full_depth,
                "upright position", upright_position_check,
                # "vertical distance", vertical_distance_hands,
                # "extension", full_extension,
                # "reps", count,
                # "no reps", no_rep
            )

            cv2.putText(img, f'reps: {int(count)}', (50, 100), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
            cv2.putText(img, f'no reps: {int(no_rep)}', (400, 100), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
            cv2.putText(img, f'outcome: {outcome}', (50, 200), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

        cv2.imshow("Image", img)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

    key = cv2.waitKey(1)
    if key == 32:  # Space bar key
        paused = not paused

    elif key == ord('q') or key == 27:  # 'q' or ESC key for quitting
        break