import cv2
import mediapipe as mp
import time


# section to use a video
mpPose = mp.solutions.pose
mpHands = mp.solutions.hands
mpFace = mp.solutions.face_mesh
mpDraw = mp.solutions.drawing_utils

# Initialize models
pose = mpPose.Pose()
hands = mpHands.Hands()
face_mesh = mpFace.FaceMesh()

video = cv2.VideoCapture(0)
pTime = 0

# Mode selector: 'pose', 'hands', or 'face'
current_mode = 'face'

while True:
    success, img = video.read()
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Process based on current mode
    if current_mode == 'pose':
        results = pose.process(imgRGB)
        if results.pose_landmarks:
            mpDraw.draw_landmarks(img, results.pose_landmarks, mpPose.POSE_CONNECTIONS)
            for id, lm in enumerate(results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(img, (cx, cy), 3, (155, 0, 0), cv2.FILLED)

    elif current_mode == 'hands':
        results = hands.process(imgRGB)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mpDraw.draw_landmarks(img, hand_landmarks, mpHands.HAND_CONNECTIONS)

    elif current_mode == 'face':
        results = face_mesh.process(imgRGB)
        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                mpDraw.draw_landmarks(img, face_landmarks, mpFace.FACEMESH_CONTOURS)

    # Calculate FPS
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime

    # Display mode and FPS
    cv2.putText(img, f"Mode: {current_mode}", (10, 30), cv2.FONT_HERSHEY_PLAIN, 2, (0, 255, 0), 2)
    cv2.putText(img, f"FPS: {int(fps)}", (10, 70), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2)

    cv2.imshow("recording", img)

    # Switch modes with keyboard
    key = cv2.waitKey(1) & 0xFF
    if key == ord('p'):
        current_mode = 'pose'
    elif key == ord('h'):
        current_mode = 'hands'
    elif key == ord('f'):
        current_mode = 'face'
    elif key == ord('q'):
        break

video.release()
cv2.destroyAllWindows()

