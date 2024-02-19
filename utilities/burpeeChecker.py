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

video = cv2.VideoCapture('../static/videos/burpee1.mp4')
pTime = 0

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
descending_threshold = 150
ascending_threshold = 150  # Threshold to indicate start of burpee i.e. standing upright
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

            # Update start and end points for the new angle range
            start_point = 170  # extended value
            end_point = 60  # full range when reached
            percentage = int(round(np.interp(angle, (end_point, start_point), (100, 0))))

            landmarks = detector.getLandmarks()

            left_hip_y = landmarks[23].y
            right_hip_y = landmarks[24].y

            # this section gets and checks the coordinates for toes (Landmarks 31 and 32)
            left_eye = [landmarks[5].x, landmarks[5].y]
            right_eye = [landmarks[2].x, landmarks[2].y]
            left_toe = [landmarks[31].x, landmarks[31].y]
            right_toe = [landmarks[32].x, landmarks[32].y]
            right_hand = [landmarks[20].x, landmarks[20].y]
            left_hand = [landmarks[19].x, landmarks[19].y]
            left_shoulder_coordinates = [landmarks[11].x, landmarks[11].y]
            right_shoulder_coordinates = [landmarks[12].x, landmarks[12].y]
            left_hip_coordinates = [landmarks[23].x, landmarks[23].y]
            right_hip_coordinates = [landmarks[24].x, landmarks[24].y]

            upright_position_check = abs((left_shoulder_coordinates[1] + right_shoulder_coordinates[1]) / 2 -
                                         (left_toe[1] + right_toe[1]) / 2)
            ####### START ANALYSIS #######
            # 1. Detect descending to the ground for start of rep
            # TODO once figured out how to tackle movement for a compount movement add to checkDirection
            # previous_angle = 0
            # direction = detector.checkDirection(
            #     angle,
            #     descending_threshold,
            #     ascending_threshold,
            #     previous_angle,
            #     downward_movement=None,
            #     compound_movement=True
            # )

            if angle < descending_threshold and not full_depth and not full_extension and not is_burpee_started:
                is_burpee_started = True
                direction = 0

                # TODO move this to a separate function in PoseModule getCurrentToeHeight
                left_toe_post_pushup = [landmarks[31].x, landmarks[31].y]
                right_toe_post_pushup = [landmarks[32].x, landmarks[32].y]

                # Calculate the average height of the toes as the new baseline
                average_toe_height_post_pushup = (left_toe_post_pushup[1] + right_toe_post_pushup[1]) / 2

            # elif angle > descending_threshold and full_depth and not full_extension and is_burpee_started:
            #     no_rep += 1
            #     outcome = "no full extension"
            #     is_burpee_started = False
            #     full_depth = False
            # elif angle > descending_threshold and not full_depth and full_extension and is_burpee_started:
            #     is_burpee_started = False
            #     no_rep += 1
            #     outcome = "no full depth"

            # 2. Detect push-up phase
            if direction == 0:
                # checks distance between x coordinates of the shoulders and feet
                # if they are inline then set full_depth to True
                pushup_depth_check = abs((left_shoulder_coordinates[1] + right_shoulder_coordinates[1]) / 2 -
                                                (left_toe[1] + right_toe[1]) / 2)
                if pushup_depth_check < pushup_threshold:
                    full_depth = True
                    direction = 1

            # 3. Detect ascending back to standing
            if direction == 1 and is_burpee_started and full_depth:
                # check body is straight first before jump or full extension
                if angle > extended_body_angle and upright_position_check > 0.2:
                    # .4 detect hands above head only when full extension is reached
                    vertical_distance_hands = abs((left_hand[1] + right_hand[1]) / 2 - (left_eye[1] + right_eye[1]) / 2)

                    # TODO move this to a separate function in PoseModule getCurrentToeHeight
                    # .5 detect jump phase
                    left_toe_current = [landmarks[31].x, landmarks[31].y]
                    right_toe_current = [landmarks[32].x, landmarks[32].y]

                    # Calculate the difference between toe starting position and current position
                    average_toe_height_current = (left_toe_current[1] + right_toe_current[1]) / 2
                    # print(average_toe_height_current, "baseline", average_toe_height_post_pushup, "should be more")

                    # Check for a jump by comparing the current toe height to the new baseline
                    # if these checks pass then it's a good rep so set full_extension to True
                    if average_toe_height_post_pushup > average_toe_height_current and vertical_distance_hands > 0.1:
                        full_extension = True
                    # reset parameters and add a no rep
                    # TODO move this out - have to reset after the whole process
                    # else:
                    #     no_rep += 1
                    #     outcome = "no full extension"
                    #     direction = 0
                    #     is_burpee_started = False
                    #     full_depth = False

                # if body is not straight, and they're starting to go down,
                # i.e. angle is less than previous, it's a no rep and reset parameters
                # elif angle < previous_angle:
                #     no_rep += 1
                #     outcome = "body not straight"
                #     direction = 0
                #     is_burpee_started = False
                #     full_depth = False

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
                int(angle),
                direction,
                outcome,
                "burpee started", is_burpee_started,
                "full depth", full_depth,
                # "upright position", upright_position_check,
                "vertical distance", vertical_distance_hands,
                "extension", full_extension,
                "reps", count,
                "no reps", no_rep
            )

            cv2.putText(img, f'reps: {int(count)}', (50, 100), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)
            # cv2.putText(img, f'{int(percentage)} %', (50, 300), cv2.FONT_HERSHEY_PLAIN, 7, (0,0,255), 8)
            cv2.putText(img, f'no reps: {int(no_rep)}', (500, 100), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)
            cv2.putText(img, f'outcome: {outcome}', (50, 200), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

        cv2.imshow("Image", img)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

    key = cv2.waitKey(1)
    if key == 32:  # Space bar key
        paused = not paused

    elif key == ord('q') or key == 27:  # 'q' or ESC key for quitting
        break