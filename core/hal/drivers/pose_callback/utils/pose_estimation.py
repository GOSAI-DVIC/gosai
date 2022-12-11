# Source : https://google.github.io/mediapipe/solutions/pose.html

import cv2
import mediapipe as mp
from os import path
import json

flip = False

def init():
    global flip
    mp_holistic = mp.solutions.holistic
    if path.exists("home/config.json"):
            with open("home/config.json", "r") as f:
                config = json.load(f)
                if ("flip" in config["camera"]): 
                    if config["camera"]["flip"] == True:
                        flip = True
    return mp_holistic.Holistic(
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5,
        smooth_landmarks=True,
        model_complexity=0,
        refine_face_landmarks = True,
    )

def landmarks_to_array(landmarks):
    landmark_array = []
    for landmark in landmarks:
        landmark_array.append(landmark.x)
        landmark_array.append(landmark.y)
        landmark_array.append(landmark.z)
    return landmark_array

def landmarks_to_array_mirror(landmarks,  min_width, width, height):
    landmark_array = [
        [
            min_width + int(landmark.x * width),
            int(landmark.y * height),
            round(landmark.visibility, 2),
        ]
        for landmark in landmarks
    ]
    return landmark_array

def find_all_poses(holistic, frame, window):
    image = frame.copy()

    min_width, max_width = int((0.5 - window / 2) * frame.shape[1]), int(
        (0.5 + window / 2) * frame.shape[1]
    )

    if flip:
        image = cv2.flip(image, 1)
                
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    # e1 = time.time()
    # print(f"    Convert image: {(e1 - start)*1000} ms")

    image.flags.writeable = False

    results = holistic.process(image)
    
    body_landmarks = landmarks_to_array_mirror(results.pose_landmarks.landmark, min_width, image.shape[1], image.shape[0]) if results.pose_landmarks else []
    left_hand_landmarks = landmarks_to_array_mirror(results.left_hand_landmarks.landmark, min_width, image.shape[1], image.shape[0]) if results.left_hand_landmarks else []
    right_hand_landmarks = landmarks_to_array_mirror(results.right_hand_landmarks.landmark, min_width, image.shape[1], image.shape[0]) if results.right_hand_landmarks else []
    
    # print(len(body_landmarks))
    return {
        "body_pose": body_landmarks, # [[x, y, visibility]]
        "right_hand_pose": left_hand_landmarks, # [[x, y, visibility]]
        "left_hand_pose": right_hand_landmarks, # [[x, y, visibility]]
    }

def find_all_poses_cables(holistic, frame):
    image = frame.copy()

    if flip:
        image = cv2.flip(image, 1)
                
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    image.flags.writeable = False

    results = holistic.process(image)
    
    body_landmarks_cables = landmarks_to_array(results.pose_landmarks.landmark) if results.pose_landmarks else []
    # left_hand_landmarks = landmarks_to_array(results.left_hand_landmarks.landmark) if results.left_hand_landmarks else []
    # right_hand_landmarks = landmarks_to_array(results.right_hand_landmarks.landmark) if results.right_hand_landmarks else []
    
    return {
        "body_pose_cables": body_landmarks_cables, # [x, y, z, x, y, z, ...]
    }