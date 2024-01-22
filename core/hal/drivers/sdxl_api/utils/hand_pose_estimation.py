# Source : https://google.github.io/mediapipe/solutions/hands.html
import cv2
import json
from google.protobuf.json_format import MessageToDict
import mediapipe as mp
from os import path
import numpy as np
import time

flip = False
rotation = 0
poolFocus_matrix = None

def init():
    global flip
    global rotation
    global poolFocus_matrix
    mp_hands = mp.solutions.hands
    if path.exists("home/config.json"):
            with open("home/config.json", "r") as f:
                config = json.load(f)
                if ("flip" in config["camera"]):
                    if config["camera"]["flip"] == True:
                        flip = True
                if ("rotation" in config["camera"]):
                    if config["camera"]["rotation"] %90 == 0:
                        rotation = config["camera"]["rotation"]
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
    return mp_hands.Hands(
        min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=0, max_num_hands=2
    )


def find_all_hands(hands, frame, window):
    # start_t = int(time.time()*1000)

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
    if rotation == 90:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
    elif rotation == 180:
        image = cv2.rotate(image, cv2.ROTATE_180)
    elif rotation == 270:
        image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)


    # e1 = time.time()
    # print(f"    Convert image: {(e1 - start)*1000} ms")

    image.flags.writeable = False

    results = hands.process(image)

    # e2 = time.time()
    # print(f"    Infer image: {(e2 - e1)*1000} ms")

    hands_landmarks = []

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            hands_landmarks.append([])
            for j, landmark in enumerate(hand_landmarks.landmark):
                # for landmark in results.multi_hand_landmarks.landmark:
                hands_landmarks[-1].append(
                    [
                        landmark.x + (1 - window) / 2,
                        landmark.y,
                    ]
                )

    hands_handedness = []

    if results.multi_handedness:
        for hand_handedness in results.multi_handedness:
            handedness_dict = MessageToDict(hand_handedness)["classification"][0]
            # print(handedness_dict)
            hands_handedness.append(
                [handedness_dict["index"], handedness_dict["label"], handedness_dict["score"]]
            )

    # e3 = time.time()
    # print(f"    Convert data: {(e3 - e2)*1000} ms")

    return {
        "hands_landmarks": hands_landmarks,
        "hands_handedness": hands_handedness,
        # "time": start_t# int(time.time()*1000),
    }
