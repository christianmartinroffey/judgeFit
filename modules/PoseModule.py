import cv2
import mediapipe as mp
import time
import math


class PoseDetector:

    def __init__(self, mode=False, model_complexity=1,
                 smooth_landmarks=True,
                 enable_segmentation=False,
                 smooth_segmentation=True,
                 detectionConfidence=0.5,
                 trackingConfidence=0.5):

        self.mode = mode
        self.model_complexity = model_complexity
        self.smooth_landmarks = smooth_landmarks
        self.enable_segmentation = enable_segmentation
        self.smooth_segmentation = smooth_segmentation
        self.detectionConfidence = detectionConfidence
        self.trackingConfidence = trackingConfidence

        self.mpPose = mp.solutions.pose
        self.mpDraw = mp.solutions.drawing_utils
        self.pose = self.mpPose.Pose(self.mode, self.model_complexity,
                                     self.smooth_landmarks, self.enable_segmentation,
                                     self.smooth_segmentation, self.detectionConfidence,
                                     self.trackingConfidence)

    def getPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
        self.results = self.pose.process(imgRGB)
        # print(results.pose_landmarks)

        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks, self.mpPose.POSE_CONNECTIONS)

        return img

    def getPosition(self, img, draw=True):
        self.lmList = []
        if self.results.pose_landmarks:
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                self.lmList.append([id, cx, cy])
                if draw:
                    cv2.circle(img, (cx, cy), 3, (255, 0, 0), cv2.FILLED)
        return self.lmList

    def getAngle(self, img, p1, p2, p3, draw=True):
        '''this is to get the angle between 3 points'''
        # same but without slicing
        _, x1, y1 = self.lmList[p1]

        # get the points
        x1, y1 = self.lmList[p1][1:]
        x2, y2 = self.lmList[p2][1:]
        x3, y3 = self.lmList[p3][1:]

        # calculate the angle
        angle = math.degrees(math.atan2(y3-y2, x3-x2) - math.atan2(y1-y2, x1-x2))

        if angle < 0:
            angle += 360
            # print(angle)

        if draw:
            # draws white line from points for visibility
            cv2.line(img, (x1, y1), (x2, y2), (255, 255, 255), 3)
            cv2.line(img, (x3, y3), (x2, y2), (255, 255, 255), 3)
            # creates a target shape for the point
            cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x1, y1), 15, (0, 0, 255), 2)
            cv2.circle(img, (x2, y2), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (0, 0, 255), 2)
            cv2.circle(img, (x3, y3), 10, (0, 0, 255), cv2.FILLED)
            cv2.circle(img, (x3, y3), 15, (0, 0, 255), 2)
            cv2.putText(
                img,
                str(int(angle)),
                (x2 + 100, y2),
                cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 4
            )
        return angle


def main():
    video = cv2.VideoCapture('../videos/airsquat.mp4')
    pTime = 0
    detector = PoseDetector()

    while True:
        success, img = video.read()
        img = detector.getPose(img)
        lmList = detector.getPosition(img, draw=False)
        if len(lmList) != 0:
            print(lmList[24])
            cv2.circle(img, (lmList[24][1], lmList[24][2]), 15, (0, 255, 0), cv2.FILLED)
        # detector.checkSquat(img)
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (70, 50), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0,), 3)
        cv2.imshow("recording", img)
        cv2.waitKey(1)


if __name__ == '__main__':
    main()
