# Source : https://google.github.io/mediapipe/solutions/hands.html
import cv2
import json
from google.protobuf.json_format import MessageToDict
import mediapipe as mp
from os import path
import numpy as np
import time

flip = False
poolFocus_matrix = None
# base_options = python.BaseOptions(model_asset_path='face_landmarker_v2_with_blendshapes.task',

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode
options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path='core/hal/drivers/hand_pose/utils/hand_landmarker.task',  delegate=mp.tasks.BaseOptions.Delegate.GPU),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=5
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
    return HandLandmarker.create_from_options(options)


def find_all_hands(hands, frame, window):
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

    hands_landmarks = []
    hands_handedness = []

    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)

    frame_ms += 33
    results = hands.detect_for_video(mp_image, frame_ms)

    if results.hand_landmarks:
        for hand_landmarks in results.hand_landmarks:
            hands_landmarks.append([])
            for _, landmark in enumerate(hand_landmarks):
                # for landmark in results.multi_hand_landmarks.landmark:
                hands_landmarks[-1].append(
                    [
                        landmark.x + (1 - window) / 2,
                        landmark.y,
                        landmark.z,
                    ]
                )

    if results.handedness:
        for hand_handedness in results.handedness:
            hand_handedness = hand_handedness[0]
            # print(handedness_dict)
            hands_handedness.append(
                [hand_handedness.index, hand_handedness.display_name, hand_handedness.score]
            )

    # except Exception as e:
    #     pass

    return {
        "hands_landmarks": hands_landmarks,
        "hands_handedness": hands_handedness,
        "frame_size": [frame.shape[1], frame.shape[0]],
        # "time": start_t# int(time.time()*1000),
    }
