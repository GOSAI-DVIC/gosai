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
FaceDetector = mp.tasks.vision.FaceDetector
FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = FaceDetectorOptions(
    base_options=BaseOptions(model_asset_path='core/hal/drivers/face_detection/utils/blaze_face_short_range.tflite',  delegate=mp.tasks.BaseOptions.Delegate.GPU),
    running_mode=VisionRunningMode.VIDEO,
    min_detection_confidence=0.9
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
    return FaceDetector.create_from_options(options)


def estimate(detector, frame, window):
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

    faces_detections = []

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)

    frame_ms += 33
    results = detector.detect_for_video(mp_image, frame_ms)

    if results.detections:
        for detection in results.detections:
            faces_detections.append([])
            for j, keypoint in enumerate(detection.keypoints):

                faces_detections[-1].append(
                    [
                        keypoint.x + (1 - window) / 2,
                        keypoint.y,

                    ]
                )

    return {
        "faces_detections": faces_detections,
        "frame_size": [frame.shape[1], frame.shape[0]],
        # "time": start_t# int(time.time()*1000),
    }
