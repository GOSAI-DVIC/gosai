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

def landmarks_to_array(landmarks,  min_width, width, height):
    landmark_array = [
        [
            min_width + int(landmark.x * width),
            int(landmark.y * height),
            round(landmark.visibility, 2),
        ]
        for landmark in landmarks
    ]
    return landmark_array


def world_landmarks_to_array(landmarks, window=1):
    landmark_array = [
        [
            landmark.x,
            landmark.y,
            landmark.z,
            round(landmark.visibility, 2),
        ]
        for landmark in landmarks
    ]
    return landmark_array


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

    face_landmarks = landmarks_to_array(results.face_landmarks.landmark, min_width, image.shape[1], image.shape[0]) if results.face_landmarks else []
    body_landmarks = landmarks_to_array(results.pose_landmarks.landmark, min_width, image.shape[1], image.shape[0]) if results.pose_landmarks else []
    left_hand_landmarks = landmarks_to_array(results.left_hand_landmarks.landmark, min_width, image.shape[1], image.shape[0]) if results.left_hand_landmarks else []
    right_hand_landmarks = landmarks_to_array(results.right_hand_landmarks.landmark, min_width, image.shape[1], image.shape[0]) if results.right_hand_landmarks else []
    body_wolrd_landmarks = world_landmarks_to_array(results.pose_world_landmarks.landmark, window) if results.pose_world_landmarks else []

    return {
        "face_mesh": face_landmarks, # [[x, y, visibility]]
        "body_pose": body_landmarks, # [[x, y, visibility]]
        "right_hand_pose": left_hand_landmarks, # [[x, y, visibility]]
        "left_hand_pose": right_hand_landmarks, # [[x, y, visibility]]
        "body_world_pose": body_wolrd_landmarks, # [[x, y, z, visibility]]
    }
