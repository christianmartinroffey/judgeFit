import cv2
import mediapipe as mp
import time

# section to access camera
# camera = cv2.VideoCapture(0)
#
# mpHands = mp.solutions.hands
# hands = mpHands.Hands()
#
# if not camera.isOpened():
#     print("Error: Could not open video capture.")
#     exit()
#
# while True:
#     success, img = camera.read()
#     if success:
#         cv2.imshow("image", img)
#         if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to quit the loop
#             break
#     else:
#         print("Error: Failed to read frame.")
#         break
#
# camera.release()
# cv2.destroyAllWindows()

# section to use a video
mpPose = mp.solutions.pose
mpDraw = mp.solutions.drawing_utils
pose = mpPose.Pose()

#video = cv2.VideoCapture('../static/videos/overhead_squat_person.mp4')
video = cv2.VideoCapture(0)
pTime = 0

while True:
    success, img = video.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
    results = pose.process(imgRGB)
    # print(results.pose_landmarks)

    if results.pose_landmarks:
        mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
        for id, lm in enumerate(results.pose_landmarks.landmark):
            h, w, c = img.shape
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(img, (cx, cy), 3, (255,0,0), cv2.FILLED)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255,0,0,), 3)
    cv2.imshow("recording", img)
    cv2.waitKey(1)



