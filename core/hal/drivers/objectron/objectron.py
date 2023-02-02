# Pose estimation Driver

import time
import numpy as np
import core.hal.drivers.object_detection.utils.find_obj as find_obj
from core.hal.drivers.driver import BaseDriver
from os import path
import json
import cv2
import mediapipe as mp
mp_drawing = mp.solutions.drawing_utils
mp_objectron = mp.solutions.objectron


class Driver(BaseDriver):
    """
    * Object detection from mediapipe
    ! Only one instance from mediapipe can run
    """

    def __init__(self, name: str, parent, max_fps: int = 60):
        super().__init__(name, parent)

        self.register_to_driver("camera", "color")
        self.create_event("raw_data")

        self.debug_time = False
        self.debug_data = False
        self.fps = max_fps
        if path.exists("home/config.json"):
            with open("home/config.json", "r") as f:
                config = json.load(f)
                if ("window" in config["screen"]): 
                    self.window = config["screen"]["window"]
                else :
                    self.window = 0.7

    def loop(self):
        frame = self.parent.get_driver_event_data("camera", "color")

        if frame is not None:
            image = frame.copy()
            min_width, max_width = int((0.5 - self.window / 2) * frame.shape[1]), int(
                (0.5 + self.window / 2) * frame.shape[1]
            )
                        
            image = image[:, min_width:max_width]

            with mp_objectron.Objectron(static_image_mode=False,
                max_num_objects=2,
                min_detection_confidence=0.2,
                min_tracking_confidence=0.2,
                model_name='Cup') as objectron:

                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                image.flags.writeable = False
                results = objectron.process(image)
                image.flags.writeable = True

                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
                image.flags.writeable = True

                if results.detected_objects:
                    for detected_object in results.detected_objects:
                        mp_drawing.draw_landmarks(
                            image, detected_object.landmarks_2d, mp_objectron.BOX_CONNECTIONS)
                        mp_drawing.draw_axis(image, detected_object.rotation,
                                            detected_object.translation)
                # Flip the image horizontally for a selfie-view display.
                cv2.imshow('MediaPipe Objectron', cv2.flip(image, 1))
                cv2.waitKey(int(100/self.fps))