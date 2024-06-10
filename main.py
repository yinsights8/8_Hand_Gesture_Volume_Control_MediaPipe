from utils.HandTrackingModule import HandDetector
import numpy as np
import time
import cv2
import math

from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

#####################################################
Wcam, Hcam = 640, 480
#####################################################

cam = cv2.VideoCapture(0)
cam.set(3, Wcam)
cam.set(4, Hcam)

hand = HandDetector()

cTime = 0
pTime = 0

###############################################################################################################################################

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = interface.QueryInterface(IAudioEndpointVolume)
# volume.GetMute()
# print(volume.GetMasterVolumeLevel())

Volume = volume.GetVolumeRange()
# volume.SetMasterVolumeLevel(0.0, None)

# get the volumn range
MinVol = Volume[0]
MaxVol = Volume[1]
###############################################################################################################################################

VolBar = 400
VolPer = 0
while True:
    succ, image = cam.read()

    image = hand.findHands(image)
    landMarks = hand.findLandMarks(image, draw=False)
    if len(landMarks) != 0:

        x1, y1 = landMarks[4][1], landMarks[4][2]
        x2, y2 = landMarks[8][1], landMarks[8][2]
        # center of the line
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        cv2.circle(image, (x1, y1), 10, (255, 0, 255), cv2.FILLED)
        cv2.circle(image, (x2, y2), 10, (255, 0, 255), cv2.FILLED)
        # create line between points
        cv2.line(image, pt1=(x1, y1), pt2=(x2, y2), color=(255, 0, 0), thickness=1)
        cv2.circle(image, (cx, cy), 8, (255, 0, 255), cv2.FILLED)

        # calculate the lenght of the line
        length = math.hypot(x2 - x1, y2 - y1)

        # Convert the values
        # Our Volumn range : 50, 300
        # volume           : -63.5,  0.0
        SetVol = np.interp(length, [50, 200], [MinVol, MaxVol])  # To Control the volume
        VolBar = np.interp(length, [50, 200], [400, 150])  # To display the Bar
        # VolPer = np.interp(length, [50, 300], [0, 100])  # To display the percentage
        VolPer = np.interp(length, [50, 200], [0, 100])  # To display the percentage

        if length < 25:
            cv2.circle(image, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
        volume.SetMasterVolumeLevel(SetVol, None)

    cv2.rectangle(image, (50, 150), (70, 400), (255, 0, 0), 3)
    cv2.rectangle(image, (50, int(VolBar)), (70, 400), (255, 0, 0), cv2.FILLED)
    cv2.putText(image, f"{int(VolPer)} %", (40, 450), 1, 2,
                (255, 0, 0), 1, cv2.FONT_HERSHEY_SCRIPT_SIMPLEX)

    ################################################################# CalCulate FPS ################################################################################
    cTime = time.time()
    FPS = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(image, f"FPS: {int(FPS)}", (50, 50), 1, 2, (255, 0, 255), 1, cv2.FONT_HERSHEY_SCRIPT_SIMPLEX)
    ################################################################# CalCulate FPS ################################################################################

    cv2.imshow("Image", image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
