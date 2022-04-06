# Source : https://google.github.io/mediapipe/solutions/hands.html
import time

import cv2
import mediapipe as mp
from google.protobuf.json_format import MessageToDict


def init():
    mp_hands = mp.solutions.hands
    return mp_hands.Hands(
        min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=0, max_num_hands=2
    )


def find_all_hands(hands, frame, window):
    # start_t = int(time.time()*1000)

    image = frame.copy()

    min_width, max_width = int((0.5 - window / 2) * frame.shape[1]), int(
        (0.5 + window / 2) * frame.shape[1]
    )
    image = image[:, min_width:max_width]

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image = cv2.flip(image, 1)

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
