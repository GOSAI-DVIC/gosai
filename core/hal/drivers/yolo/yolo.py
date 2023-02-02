# Object Detection Driver

import time
from core.hal.drivers.driver import BaseDriver
from os import path
import json
from ultralytics import YOLO
import cv2


flip = False

class Driver(BaseDriver):
    """
    * Object detection from YoloV8
    """

    def __init__(self, name: str, parent, max_fps: int = 60):
        super().__init__(name, parent)
        print("Object Detection Driver Loaded")

        self.register_to_driver("camera", "color")
        self.create_event("detected_objects")

        self.debug_time = False
        self.debug_data = False
        self.fps = max_fps

        global flip

        if path.exists("home/config.json"):
            with open("home/config.json", "r") as f:
                config = json.load(f)
                if ("window" in config["screen"]): 
                    self.window = config["screen"]["window"]
                else :
                    self.window = 0.7
                
                if ("flip" in config["camera"]): 
                        if config["camera"]["flip"] == True:
                            flip = True

    def pre_run(self):
        super().pre_run()

        self.model = YOLO("model.pt")

    def loop(self):
        start_t = time.time()

        color = self.parent.get_driver_event_data("camera", "color")

        if color is not None:
            object_data = self.find_all_poses(self.model, color, self.window)

            flag_1 = time.time()
            self.set_event_data("detected_objects", object_data)

            if self.debug_data:
                self.log(object_data)

            if self.debug_time:
                self.log(f"Inference: {(flag_1 - start_t)*1000} ms")

        else:
            self.log("No color data", 1)

        end_t = time.time()

        if self.debug_time:
            self.log(f"Total time: {(end_t - start_t)*1000}ms")
            self.log(f"FPS: {int(1/(end_t - start_t))}")


    def landmarks_to_array(landmarks, min_width, width, height):
        landmark_array = [
            [
                min_width + int(landmark.x * width),
                int(landmark.y * height),
                round(landmark.visibility, 2),
            ]
            for landmark in landmarks
        ]
        return landmark_array

    def find_all_poses(model, frame, window):
        # start = time.time()

        image = frame.copy()

        min_width, max_width = int((0.5 - window / 2) * frame.shape[1]), int(
            (0.5 + window / 2) * frame.shape[1]
        )
        
        if flip:
            image = cv2.flip(image, 1)
                    
        image = image[:, min_width:max_width]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        image.flags.writeable = False

        results = model.predict(source=image, save=True, save_txt=True)

        # face_landmarks = landmarks_to_array(results.face_landmarks.landmark, min_width, image.shape[1], image.shape[0]) if results.face_landmarks else []
        print(results)

        return {
            "boxes": results.boxes,
            "masks": results.masks,
            "probs": results.probs,
            "orig_shape": results.orig_shape,
        }
