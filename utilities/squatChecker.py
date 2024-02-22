import cv2
import numpy as np
import mediapipe as mp
import PoseModule as pm
from utilities.utils import load_movement_criteria


criteria = load_movement_criteria()  # Load criteria from JSON file

squat_criteria = criteria.get('squat', {})
descending_threshold = squat_criteria.get('descending_threshold', 110)  # Default if not found
ascending_threshold = squat_criteria.get('ascending_threshold', 110)  # Default if not found
# video = cv2.VideoCapture(1)
video = cv2.VideoCapture('../static/videos/airsquat.mp4')
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
previous_angle = 0
paused = False

while True:
    if not paused:
        success, img = video.read()
        img = detector.getPose(img, draw=False)

        lmList = detector.getPosition(img, draw=False)
        if len(lmList) != 0:
            # Choose landmarks based on hip visibility
            # determine the best landmarks to use
            hip_index, knee_index, ankle_index = detector.getLandmarkIndices(lmList, is_squat=True)

            # Calculate the angle for the squat analysis
            angle = detector.getAngle(img, hip_index, knee_index, ankle_index)
            direction = detector.checkDirectionFromAngle(
                angle,
                descending_threshold,
                ascending_threshold,
                previous_angle,
                downward_movement=True
            )

            # Update start and end points for the new angle range
            start_point = squat_criteria.get('start_point', 165)  # Default if not found
            end_point = squat_criteria.get('end_point', 60)
               # extended value

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
                "no reps", no_rep,
                is_squat_started
            )

            cv2.putText(img, f'reps: {int(count)}', (50, 100), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 5)
            cv2.putText(img, f'no reps: {int(no_rep)}', (500, 100), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 5)
            cv2.putText(img, f'outcome: {outcome}', (50, 200), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 5)

        cv2.imshow("Image", img)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

    key = cv2.waitKey(1)
    if key == 32:  # Space bar key
        paused = not paused

    elif key == ord('q') or key == 27:  # 'q' or ESC key for quitting
        break
