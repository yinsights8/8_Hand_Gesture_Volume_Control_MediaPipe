import cv2
import cvzone
import numpy as np
import time
import cv2
import math
from utils.HandTrackingModule import HandDetector
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume



class Detector:
    def __init__(self, videoPath, target_video_width = 640):
        self.videoPath = videoPath

        self.hand = HandDetector()
        self.cam = cv2.VideoCapture(self.videoPath)

        self.cTime = 0
        self.pTime = 0

        self.VolBar = 400
        self.VolPer = 0
        
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(
            IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.volume = interface.QueryInterface(IAudioEndpointVolume)
        # volume.GetMute()
        # print(volume.GetMasterVolumeLevel())

        Volume = self.volume.GetVolumeRange()
        # volume.SetMasterVolumeLevel(0.0, None)

        # get the volumn range
        self.MinVol = Volume[0]
        self.MaxVol = Volume[1]

        # Get original video width and height
        self.original_width = int(self.cam.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.original_height = int(self.cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # Calculate the aspect ratio
        aspect_ratio = self.original_width / self.original_height

        # Set the target width and height
        self.target_width = target_video_width
        self.target_height = int(self.target_width / aspect_ratio)

        # Define the codec and create VideoWriter object
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        self.out = cv2.VideoWriter('output_video.mp4', fourcc, 30.0, (self.target_width, self.target_height))

    # video will automatically turn off after closing website
    def __del__(self):
        return self.cam.release()


    
    def outputFrames(self):
        """
        This function is use to display the predictions on live video
        This function can be use when predicting on live fotage
        """
        # while True:
        succ, image = self.cam.read()
        resized_frame = cv2.resize(image, (self.target_width, self.target_height))

        image = self.hand.findHands(resized_frame)
        landMarks = self.hand.findLandMarks(resized_frame, draw=False)
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
            # min_vol, min_vol = self.AudioUtilities()
            self.SetVol = np.interp(length, [50, 200], [self.MinVol, self.MaxVol])  # To Control the volume
            self.VolBar = np.interp(length, [50, 200], [400, 150])  # To display the Bar
            # VolPer = np.interp(length, [50, 300], [0, 100])  # To display the percentage
            self.VolPer = np.interp(length, [50, 200], [0, 100])  # To display the percentage

            if length < 25:
                cv2.circle(image, (cx, cy), 5, (0, 0, 255), cv2.FILLED)
            self.volume.SetMasterVolumeLevel(self.SetVol, None)

        cv2.rectangle(image, (50, 150), (70, 400), (255, 0, 0), 3)
        cv2.rectangle(image, (50, int(self.VolBar)), (70, 400), (255, 0, 0), cv2.FILLED)
        cv2.putText(image, f"{int(self.VolPer)} %", (40, 450), 1, 2,
                    (255, 0, 0), 1, cv2.FONT_HERSHEY_SCRIPT_SIMPLEX)

        ################################################################# CalCulate FPS ################################################################################
        self.cTime = time.time()
        FPS = 1 / (self.cTime - self.pTime)
        self.pTime = self.cTime
        cv2.putText(image, f"FPS: {int(FPS)}", (50, 50), 1, 2, (255, 0, 255), 1, cv2.FONT_HERSHEY_SCRIPT_SIMPLEX)
        ################################################################# CalCulate FPS ################################################################################

    ####################################################################################################################
        self.out.write(resized_frame)
        ret, buffer = cv2.imencode(".jpg", resized_frame)
        frame = buffer.tobytes()

        return frame