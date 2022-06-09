# Source : https://google.github.io/mediapipe/solutions/pose.html

import cv2
import mediapipe as mp


def init():
    mp_holistic = mp.solutions.holistic
    return mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        smooth_landmarks=True,
        model_complexity=0,
    )


def find_all_poses(holistic, frame, window):
    # start = time.time()

    image = frame.copy()

    min_width, max_width = int((0.5 - window / 2) * frame.shape[1]), int(
        (0.5 + window / 2) * frame.shape[1]
    )
    image = cv2.flip(image, 1)
    image = image[:, min_width:max_width]
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # e1 = time.time()
    # print(f"    Convert image: {(e1 - start)*1000} ms")

    image.flags.writeable = False

    results = holistic.process(image)

    # e2 = time.time()
    # print(f"    Infer image: {(e2 - e1)*1000} ms")

    body_landmarks = []

    if results.pose_landmarks:
        body_landmarks = [
            [
                (0.5 - window / 2) + landmark.x * window,
                landmark.y,
                round(landmark.visibility, 2),
            ]
            for landmark in results.pose_landmarks.landmark
        ]

    faces_landmarks = []

    if results.face_landmarks:
        faces_landmarks = [
            [
                (0.5 - window / 2) + landmark.x * window,
                landmark.y,
                round(landmark.visibility, 2),
            ]
            for landmark in results.face_landmarks.landmark
        ]

    left_hands_landmarks = []

    if results.left_hand_landmarks:
        left_hands_landmarks = [
            [
                (0.5 - window / 2) + landmark.x * window,
                landmark.y,
                round(landmark.visibility, 2),
            ]
            for landmark in results.left_hand_landmarks.landmark
        ]

    right_hands_landmarks = []

    if results.right_hand_landmarks:
        right_hands_landmarks = [
            [
                (0.5 - window / 2) + landmark.x * window,
                landmark.y,
                round(landmark.visibility, 2),
            ]
            for landmark in results.right_hand_landmarks.landmark
        ]

    # e3 = time.time()
    # print(f"    Convert data: {(e3 - e2)*1000} ms")

    return {
        "face_mesh": faces_landmarks,
        "body_pose": body_landmarks,
        "right_hand_pose": left_hands_landmarks,
        "left_hand_pose": right_hands_landmarks,
    }
