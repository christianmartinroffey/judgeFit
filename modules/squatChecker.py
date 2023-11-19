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

    # resize the video
    # img = cv2.resize(img, (1280, 720))

    # use an image instead of video above
    # img = cv2.imread('../images/full_squat.jpg')
    img = detector.getPose(img, draw=False)

    lmList = detector.getPosition(img, draw=False)
    if len(lmList) != 0:
        # TODO check when they're facing front or back
        left_shoulder_x = lmList[11][1]  # The second element in the list is the X-coordinate
        right_shoulder_x = lmList[12][1]
        left_hip = lmList[23][1]
        right_hip = lmList[24][1]
        nose_x = lmList[0][1]
        left_heel_x = lmList[29][1]
        right_heel_x = lmList[30][1]

        # Determine the orientation using shoulders
        shoulder_based_left = left_shoulder_x < right_shoulder_x
        shoulder_based_right = right_shoulder_x < left_shoulder_x

        # Determine the orientation using shoulders and hips
        hip_based_left = left_shoulder_x < left_hip
        hip_based_right = right_shoulder_x < right_hip

        # Determine the orientation using heels and nose
        heel_based_left = abs(nose_x - left_heel_x) < abs(nose_x - right_heel_x)
        heel_based_right = abs(nose_x - right_heel_x) < abs(nose_x - left_heel_x)

        # Assign orientation
        if heel_based_left:
            person_is_facing_left = True
            person_is_facing_right = False
            angle = detector.getAngle(img, 23, 25, 27)
            start_point = 170
            end_point = 45
            percentage = int(round(np.interp(angle, (45, 170), (100, 0))))
        elif heel_based_right:
            person_is_facing_left = False
            person_is_facing_right = True
            angle = detector.getAngle(img, 24, 26, 28)
            start_point = 200
            end_point = 310
            percentage = int(round(np.interp(angle, (200, 300), (0, 100))))
        # else:
        #     # Ambiguous or need more analysis
        #     person_is_facing_left = False
        #     person_is_facing_right = False

        print(
            angle,
            "%", percentage,
            "start_squat", is_squat_started,
            "full depth", full_depth,
            "reps", count,
            "no reps", no_rep,
            "facing left", person_is_facing_left,
            "facing right", person_is_facing_right
        )
        # start at top i.e 100% and direction is 0 i.e going down
        if percentage == 100 and not is_squat_started:
            is_squat_started = True
            full_depth = False

        # sets direction and full_depth to True
        # TODO FIX count for facing right
        # TODO look at when is_squat_started begins to fix no rep
        if is_squat_started and direction == 0:
            outcome = ""
            if person_is_facing_left:
                if angle <= end_point:
                    # Finish the squat when returning to the starting position
                    full_depth = True
                    direction = 1
                    no_rep_reason = ""
            elif person_is_facing_right:
                if angle >= end_point:
                    full_depth = True
                    direction = 1
                    no_rep_reason = ""
                else:
                    full_depth = False

            # only adds a rep if full_depth is true and angle goes back past or to the start_point (angle)
        if full_depth and direction == 1:
            # angles for left and right are different so completed squat is >= for left and <= for right
            if person_is_facing_left and angle >= start_point:
                count += 1
                is_squat_started = False
                direction = 0
                full_depth = False
                outcome = "good rep"
            # TODO fix counting for right facing
            elif person_is_facing_right and angle <= start_point:
                # count += 1
                is_squat_started = False
                direction = 0
                full_depth = False
                outcome = "good rep"
        elif not full_depth and is_squat_started:
            # TODO FIX NO REP COUNTER
            if person_is_facing_left and angle >= start_point:
                no_rep += 1
                outcome = "not deep enough"
                is_squat_started = False
                direction = 0
            elif person_is_facing_left and angle <= start_point:
                no_rep += 1
                outcome = "not deep enough"
                is_squat_started = False
                direction = 0


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