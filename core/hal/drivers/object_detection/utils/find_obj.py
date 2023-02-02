# Source : https://google.github.io/mediapipe/solutions/pose.html

import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from os import path
import json
import numpy as np

flip = False
MARGIN = 10  # pixels
ROW_SIZE = 10  # pixels
FONT_SIZE = 1
FONT_THICKNESS = 1
TEXT_COLOR = (255, 0, 0)  # red


def init():
    global flip
    dir_path = path.dirname(path.realpath(__file__))
    base_options = python.BaseOptions(model_asset_path=path.join(dir_path, 'models/efficientdet_lite2_uint8.tflite'))
    
    options = vision.ObjectDetectorOptions(base_options=base_options,
                                        score_threshold=0.5)
    detector = vision.ObjectDetector.create_from_options(options)

    if path.exists("home/config.json"):
            with open("home/config.json", "r") as f:
                config = json.load(f)
                if ("flip" in config["camera"]): 
                    if config["camera"]["flip"] == True:
                        flip = True

    return detector

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



def visualize(
    image,
    detection_result
) -> np.ndarray:
  """Draws bounding boxes on the input image and return it.
  Args:
    image: The input RGB image.
    detection_result: The list of all "Detection" entities to be visualize.
  Returns:
    Image with bounding boxes.
  """
  for detection in detection_result.detections:
    # Draw bounding_box
    bbox = detection.bounding_box
    start_point = bbox.origin_x, bbox.origin_y
    end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
    cv2.rectangle(image, start_point, end_point, TEXT_COLOR, 3)

    # Draw label and score
    category = detection.categories[0]
    category_name = category.category_name
    probability = round(category.score, 2)
    result_text = category_name + ' (' + str(probability) + ')'
    text_location = (MARGIN + bbox.origin_x,
                     MARGIN + ROW_SIZE + bbox.origin_y)
    cv2.putText(image, result_text, text_location, cv2.FONT_HERSHEY_PLAIN,
                FONT_SIZE, TEXT_COLOR, FONT_THICKNESS)

  return image


def find_all_objects(detector, frame, window, fps):
    # start = time.time()

    image = frame.copy()

    min_width, max_width = int((0.5 - window / 2) * frame.shape[1]), int(
        (0.5 + window / 2) * frame.shape[1]
    )
                
    image = image[:, min_width:max_width]
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    mp_image = mp.ImageFrame(image_format=mp.ImageFormat.SRGB, data=image)
    print("test1")

    detection_result = detector.detect(mp_image)
    # detection_result = detector.detect(mp_image)
    print(detection_result)

    image_copy = np.copy(detection_result.numpy_view())
    annotated_image = visualize(image_copy, detection_result)
    rgb_annotated_image = cv2.cvtColor(annotated_image, cv2.COLOR_BGR2RGB)
    cv2.imshow(rgb_annotated_image)
    cv2.waitKey(int(100/fps))
    
    # face_landmarks = landmarks_to_array(results.face_landmarks.landmark, min_width, image.shape[1], image.shape[0]) if results.face_landmarks else []
    return {
        "objects": [
            {
                "id": detection.id,
                "label": detection.label,
                "score": detection.score,
                "bbox": {
                    "x": detection.bbox.xmin,
                    "y": detection.bbox.ymin,
                    "width": detection.bbox.width,
                    "height": detection.bbox.height,
                },
            }
            for detection in detection_result.detections
        ],
    }


