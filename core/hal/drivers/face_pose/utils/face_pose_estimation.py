# Source : https://google.github.io/mediapipe/solutions/faces.html
import cv2
import json
import mediapipe as mp
from os import path
import numpy as np
import time

flip = False
poolFocus_matrix = None
# base_options = python.BaseOptions(model_asset_path='face_landmarker_v2_with_blendshapes.task',

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
FaceLandmarkerResult = mp.tasks.vision.FaceLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode
options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='core/hal/drivers/face_pose/utils/face_landmarker.task',  delegate=mp.tasks.BaseOptions.Delegate.GPU),
    running_mode=VisionRunningMode.VIDEO,
    num_faces=5
)

frame_ms = 0

def init():
    global flip
    global poolFocus_matrix

    if path.exists("home/config.json"):
        with open("home/config.json", "r") as f:
            config = json.load(f)
            if ("flip" in config["camera"]):
                if config["camera"]["flip"] == True:
                    flip = True
            if ("calibrate" in config):
                if config["calibrate"] == True:
                    # Search for calibration file and load poolFocus_matrix :
                    if path.exists("home/calibration_data.json"):
                        with open("home/calibration_data.json", "r") as f:
                            calibration = json.load(f)
                            if ("poolFocus_matrix" in calibration):
                                poolFocus_matrix = np.array(calibration["poolFocus_matrix"])
                                # print(poolFocus_matrix)
                            else:
                                print("No poolFocus_matrix in calibration file")
    return FaceLandmarker.create_from_options(options)


def estimate(landmarker, frame, window):
    global frame_ms

    image = frame.copy()

    if poolFocus_matrix is not None:
        image = cv2.warpPerspective(image, poolFocus_matrix, (image.shape[1], image.shape[0]), flags=cv2.INTER_LINEAR)

    min_width, max_width = int((0.5 - window / 2) * frame.shape[1]), int(
        (0.5 + window / 2) * frame.shape[1]
    )
    image = image[:, min_width:max_width]

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    if flip:
        image = cv2.flip(image, 1)

    image.flags.writeable = False

    faces_landmarks = []

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)

    frame_ms += 33
    results = landmarker.detect_for_video(mp_image, frame_ms)

    if results.face_landmarks:
        for face_landmarks in results.face_landmarks:
            faces_landmarks.append([])
            for _, landmark in enumerate(face_landmarks):

                faces_landmarks[-1].append(
                    [
                        landmark.x + (1 - window) / 2,
                        landmark.y,
                        landmark.z,
                    ]
                )

    return {
        "faces_landmarks": faces_landmarks,
        "frame_size": [frame.shape[1], frame.shape[0]],
        # "time": start_t# int(time.time()*1000),
    }
