# Face Pose estimation Driver
import pickle
import time

import core.hal.drivers.face_detection.utils.face_detection_estimation as fde
from core.hal.drivers.driver import BaseDriver


class Driver(BaseDriver):
    """Face detection driver"""
    def __init__(self, name: str, parent):
        super().__init__(name, parent)
        self.type = "no_loop"
        self.register_to_driver("camera", "color")
        self.register_to_driver("interpolate", "interpolated_data")
        self.create_event("detected_faces")
        self.create_event("interpolated_detection")

        self.window = 1

    def pre_run(self):
        """Runs once at the start of the driver"""
        super().pre_run()

        self.detector = fde.init()
        self.start_time = time.time()
        self.create_callback_on_event("detect_face", self.detect_face, "camera", "color")
        self.create_callback_on_event("interpolate_detection", self.interpolate_detection, "interpolate", "interpolated_data")


    def detect_face(self, camera_color_frame):
        """Runs face pose estimation on camera frame"""

        if camera_color_frame is not None:
            face_detection_data = fde.estimate(self.detector, camera_color_frame, self.window)

            self.face_detection_data = face_detection_data
            self.set_event_data("detected_faces", face_detection_data)

            dt = time.time() - self.start_time
            self.start_time = time.time()

            self.db.publish(f"{'interpolate'}_exec_{'interpolate_points'}", pickle.dumps({
                "name": "interpolated_show_hands",
                "amount": 3,
                "duration": dt,
                "points": face_detection_data["faces_detections"],
                "factor": 0.5,
                "depth": 2,
            }))

    def interpolate_detection(self, data):
        """Runs face pose estimation on camera frame"""

        if data["name"] == "interpolated_show_hands":
            self.face_detection_data["faces_detections"] = data["points"]
            self.set_event_data("interpolated_detection", self.face_detection_data)
