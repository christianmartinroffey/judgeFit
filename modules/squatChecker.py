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

video = cv2.VideoCapture('../videos/wallball.mp4')
pTime = 0


detector = pm.PoseDetector()
count = 0
no_rep = 0
# 1 = up, 0 = down
direction = 0
start_point = 0
end_point = 0
is_squat_started = False
full_depth = False
outcome = ""

while True:
    success, img = video.read()
    img = detector.getPose(img, draw=False)

    lmList = detector.getPosition(img, draw=False)
    if len(lmList) != 0:
        # Calculate the angle for the squat analysis
        # Update these landmark indices based on the points you're using
        hip_index = 24  # Example hip landmark index
        knee_index = 26 # Example knee landmark index
        ankle_index = 28 # Example ankle landmark index

        angle = detector.getAngle(img, hip_index, knee_index, ankle_index)

        # Update start and end points for the new angle range
        start_point = 170  # Example value, adjust as needed
        end_point = 45     # Example value, adjust as needed
        percentage = int(round(np.interp(angle, (end_point, start_point), (100, 0))))

        # Squat analysis logic
        if percentage == 100 and not is_squat_started:
            is_squat_started = True
            full_depth = False

        if is_squat_started and direction == 0:
            if angle <= end_point:
                full_depth = True
                direction = 1
            else:
                full_depth = False

        if full_depth and direction == 1:
            if angle >= start_point:
                count += 1
                is_squat_started = False
                direction = 0
                full_depth = False
                outcome = "good rep"
        elif not full_depth and is_squat_started:
            if angle >= start_point:
                no_rep += 1
                outcome = "not deep enough"
                is_squat_started = False
                direction = 0

        # Output for debugging or display
        print(
            angle,
            "%", percentage,
            "start_squat", is_squat_started,
            "full depth", full_depth,
            "reps", count,
            "no reps", no_rep
        )
        # start at top i.e 100% and direction is 0 i.e going down
        if percentage == 100 and not is_squat_started:
            is_squat_started = True
            full_depth = False

        # sets direction and full_depth to True
        # TODO FIX count for facing right
        # TODO look at when is_squat_started begins to fix no rep
        # if is_squat_started and direction == 0:
        #     outcome = ""
        #     if person_is_facing_left:
        #         if angle <= end_point:
        #             # Finish the squat when returning to the starting position
        #             full_depth = True
        #             direction = 1
        #             no_rep_reason = ""
        #     elif person_is_facing_right:
        #         if angle >= end_point:
        #             full_depth = True
        #             direction = 1
        #             no_rep_reason = ""
        #         else:
        #             full_depth = False
        #
        #     # only adds a rep if full_depth is true and angle goes back past or to the start_point (angle)
        # if full_depth and direction == 1:
        #     # angles for left and right are different so completed squat is >= for left and <= for right
        #     if person_is_facing_left and angle >= start_point:
        #         count += 1
        #         is_squat_started = False
        #         direction = 0
        #         full_depth = False
        #         outcome = "good rep"
        #     # TODO fix counting for right facing
        #     elif person_is_facing_right and angle <= start_point:
        #         # count += 1
        #         is_squat_started = False
        #         direction = 0
        #         full_depth = False
        #         outcome = "good rep"
        # elif not full_depth and is_squat_started:
        #     # TODO FIX NO REP COUNTER
        #     if person_is_facing_left and angle >= start_point:
        #         no_rep += 1
        #         outcome = "not deep enough"
        #         is_squat_started = False
        #         direction = 0
        #     elif person_is_facing_left and angle <= start_point:
        #         no_rep += 1
        #         outcome = "not deep enough"
        #         is_squat_started = False
        #         direction = 0


        # original method
        # if percentage == 100:
        #     angle = angle
        #     print(angle)
        #     # going up
        #     if direction == 0:
        #         count += 0.5
        #         direction = 1
        # if percentage == 0:
        #     if direction == 1:
        #         count += 0.5
        #         direction = 0
        # print(count)
        cv2.putText(img, f'reps: {int(count)}', (50, 100), cv2.FONT_HERSHEY_PLAIN, 7, (255,0,0), 8)
        cv2.putText(img, f'{int(percentage)} %', (50, 300), cv2.FONT_HERSHEY_PLAIN, 7, (0,0,255), 8)
        cv2.putText(img, f'no reps: {int(no_rep)}', (50, 500), cv2.FONT_HERSHEY_PLAIN, 7, (0,0,255), 8)
        cv2.putText(img, f'outcome: {outcome}', (50, 700), cv2.FONT_HERSHEY_PLAIN, 7, (0,0,255), 8)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    results = pose.process(imgRGB)