import cv2
import numpy as np
import mediapipe as mp
import time


class HandDetector:
    def __init__(self, mode=False, NumHands=2, ModelCompx=1, detectConf=0.5, trackConf=0.5,
                 color=(0, 255, 0), circle_radius=1, thickness=2):
        self.mode = mode
        self.NumHands = NumHands
        self.ModelCompx = ModelCompx
        self.detectConf = detectConf
        self.trackConf = trackConf
        self.color = color
        self.circle_radius = circle_radius
        self.thickness = thickness

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(self.mode, self.NumHands, self.ModelCompx, self.detectConf, self.trackConf)
        self.mpDraw = mp.solutions.drawing_utils
        self.drawSpec = self.mpDraw.DrawingSpec(color=self.color, circle_radius=self.circle_radius, thickness=self.thickness)

    def findHands(self, img, draw_lm=True):
        # 2. Convert our image BGR to RGB because mideapipe only needs RGB images
        ImgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # 3. then pass the RGB image to process
        self.results = self.hands.process(ImgRGB)
        # print(results.multi_hand_landmarks)
        # Check the hand landmarks
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw_lm:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS, self.drawSpec)
        return img

    def findLandMarks(self, img, HandNum=0, draw=True):
        """
        :param draw_con: this is to draw connections on landmarks
        :return: list of id and respective positions -> [id, cx,cy]
        """
        listLm = []

        if self.results.multi_hand_landmarks:
            my_hand = self.results.multi_hand_landmarks[HandNum]
            for id, lm in enumerate(my_hand.landmark):
                # print(id, lm)
                # calculate the center position of the landmark
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                listLm.append([id, cx, cy])

                if draw:
                    cv2.circle(img, (cx, cy), 7, (255, 0, 255), cv2.FILLED)

        return listLm
        #     if id == 8:
        #         cv2.circle(img, (cx, cy), 15, (0, 0, 255), cv2.FILLED)
        # mpDraw.draw_landmarks(img, handLms, mpHands.HAND_CONNECTIONS)


def main():
    cam = cv2.VideoCapture(0)
    cTime = 0
    pTime = 0

    while True:
        success, img = cam.read()

        # create hand
        hand = HandDetector()
        img = hand.findHands(img, draw_lm=True)
        listLmarks = hand.findLandMarks(img, HandNum=1, draw=True)

        if len(listLmarks) != 0:
            print(listLmarks[5])

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, text=f"FPS: {str(int(fps))}", org=(50, 50), color=(255, 0, 0), fontFace=cv2.FONT_HERSHEY_COMPLEX,
                    fontScale=1)

        cv2.imshow("Image", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


if __name__ == "__main__":
    main()
