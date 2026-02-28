import cv2
import numpy as np
import PoseModule as pm
from workout.utilities.utils import load_movement_criteria


criteria = load_movement_criteria()

# Example for a "Toes to Bar" analysis
ttb_criteria = criteria.get('toes_to_bar', {})
descending_threshold = ttb_criteria.get('descending_threshold', 30)  # Default if not found


#video = cv2.VideoCapture('../static/videos/toestobar.MOV')
video = cv2.VideoCapture(0)

pTime = 0

detector = pm.PoseDetector()

count = 0
no_rep = 0
# 1 = up, 0 = down
direction = None
start_point = 180
end_point = 10
is_movement_started = False
full_range = False
full_extension = False
outcome = ""
descending_threshold = 30  # Threshold to indicate start of movement
ascending_threshold = 150
full_range_threshold = 10  # Adjust threshold based on your requirement in pixels
left_hand_threshold_check = 0
right_hand_threshold_check = 0
paused = False
previous_angle = 0

while True:
    if not paused:
        success, img = video.read()
        img = detector.getPose(img, draw=False)

        lmList = detector.getPosition(img, draw=False)
        if len(lmList) != 0:
            # landmarks for hands and feet to check for full range
            left_hand_y = min(lmList[19][2], lmList[17][2])
            right_hand_y = min(lmList[20][2], lmList[18][2])
            left_toe_y = lmList[31][2]
            right_toe_y = lmList[32][2]
            left_toe_x = lmList[31][1]
            right_toe_x = lmList[32][1]

            # get visibility depending on which way athlete is facing
            # determine the best landmarks to use
            shoulder_index, hip_index, ankle_index = detector.getLandmarkIndices(lmList)

            # Calculate the angle
            # Need to use the angle to check for direction of movement
            angle = detector.getAngle(img, shoulder_index, hip_index, ankle_index)
            landmarks = detector.getLandmarks()

            left_hip_y = landmarks[23].y
            right_hip_y = landmarks[24].y

            # this section gets and checks the coordinates for toes (Landmarks 31 and 32)
            left_toe = [landmarks[31].x, landmarks[31].y]
            right_toe = [landmarks[32].x, landmarks[32].y]
            right_hand = [landmarks[20].x, landmarks[20].y]
            left_hand = [landmarks[19].x, landmarks[19].y]

            # Convert coordinates to pixel values
            h, w, c = img.shape
            left_toe_pixel = np.multiply(left_toe, [w, h]).astype(int)
            right_toe_pixel = np.multiply(right_toe, [w, h]).astype(int)
            left_hand_pixel = np.multiply(left_hand, [w, h]).astype(int)
            right_hand_pixel = np.multiply(right_hand, [w, h]).astype(int)

            # Draw circles at the toe positions
            # cv2.circle(img, tuple(left_toe_pixel), 15, (255, 0, 0), -1)  # Blue circle for left toe
            # cv2.circle(img, tuple(right_toe_pixel), 15, (0, 255, 0), -1)  # Green circle
            # cv2.circle(img, tuple(left_hand_pixel), 15, (255, 0, 0), -1)  # Blue circle for left hand
            # cv2.circle(img, tuple(right_hand_pixel), 15, (0, 255, 0), -1)

            direction = detector.checkDirectionFromAngle(
                angle,
                descending_threshold,
                ascending_threshold,
                previous_angle,
                downward_movement=False
            )

            left_hand_threshold_check = abs(left_hand_y - left_toe_y)
            right_hand_threshold_check = abs(right_hand_y - right_toe_y)

            # Movement analysis logic section #
            ''' standards: 
            1. athlete starts from hanging position with feet behind bar
            2. rep is completed when the athlete's toes touch the bar 
            '''
            # start the movement check by checking that there's upward movement
            if direction == 1 and not is_movement_started:
                is_movement_started = True
                full_range = False
                full_extension = False
                outcome = ''

            # movement is going down, started and the pixel value has to be > the value the hand to be full extension
            if direction == 0 and is_movement_started:
                # check if feet are behind hands for full extension
                if left_hand[1] < left_toe[1] or right_hand[1] < right_toe[1]:
                    full_extension = True

            elif direction == 1 and is_movement_started:
                # METHOD TO USE Y COORDINATES FOR RANGE BASED ON THRESHOLD
                # if movement is going up check if hit full range
                if left_hand_threshold_check < full_range_threshold or right_hand_threshold_check < full_range_threshold:
                    full_range = True
                # Check for no full extension
                # if angle is going higher it means athlete is going up

            if direction == 0 and is_movement_started:
                if full_range:
                    if not full_extension and angle < previous_angle and direction == 1:
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

            # has to have hit full range, full extension and be moving downwards
            if full_range and full_extension and direction == 0:
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
                direction,
                outcome,
                # "extension", full_extension,
                # "full range", full_range,
                "reps", count,
                "no reps", no_rep
            )

            cv2.putText(img, f'reps: {int(count)}', (50, 100), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 3)
            cv2.putText(img, f'no reps: {int(no_rep)}', (500, 100), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
            cv2.putText(img, f'outcome: {outcome}', (50, 200), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

        cv2.imshow("Image", img)
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)

    key = cv2.waitKey(1)
    if key == 32:  # Space bar key
        paused = not paused

    elif key == ord('q') or key == 27:  # 'q' or ESC key for quitting
        break
