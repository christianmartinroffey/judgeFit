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

video = cv2.VideoCapture('../static/videos/burpee.mp4')
pTime = 0

detector = pm.PoseDetector()

count = 0
no_rep = 0
# 1 = up, 0 = down
direction = None
start_point = 0
end_point = 0
is_burpee_started = False
is_pushup_complete = False
full_extension = False  # set when athlete has jumped
full_depth = None  # set alongside pushup_complete
outcome = ""
descending_threshold = 170  # Threshold to indicate start of burpee i.e. standing upright
ascending_threshold = 110
paused = False


while True:
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

        # Calculate angles or positions for different phases
        # For descending and ascending, check hip and shoulder position
        # For push-up, check the angle or distance between shoulders and hips
        # For jump, monitor the y-coordinate of the head or shoulders

        # 3. Detect ascending back to standing
        # 4. Detect jump phase

        # Update start and end points for the new angle range
        start_point = 170  # extended value
        end_point = 60  # full range when reached
        percentage = int(round(np.interp(angle, (end_point, start_point), (100, 0))))

        # 1. Detect descending to the ground
        if angle < descending_threshold and not is_pushup_complete:
            direction = 0

        # 2. Detect push-up phase
        # this option is based on the angle of the elbow
        # TODO check if using coordinates is better
        if direction == 0 and push_up_angle > 60:
            is_pushup_complete = True

        # movement analysis logic
        if direction == 0 and angle > descending_threshold:
            if not is_burpee_started:
                is_burpee_started = True
                full_depth = False
                full_extension = False

            # get the position of the toes and check if shoulder is at the same level
            if angle <= end_point:
                full_depth = True

        elif direction == 1 and is_burpee_started:
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
                        is_burpee_started = False
            elif not full_depth:
                # if didn't reach full depth and they start going up
                if angle > previous_angle and full_extension:
                    no_rep += 1
                    outcome = "not deep enough"
                    direction = 1
                    is_burpee_started = False

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
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

    key = cv2.waitKey(1)
    if key == 32:  # Space bar key
        paused = not paused

    elif key == ord('q') or key == 27:  # 'q' or ESC key for quitting
        break