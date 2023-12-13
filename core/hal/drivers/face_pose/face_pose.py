# Face Pose estimation Driver

import core.hal.drivers.face_pose.utils.face_pose_estimation as fpe
from core.hal.drivers.driver import BaseDriver


class Driver(BaseDriver):
    """Hand pose driver"""
    def __init__(self, name: str, parent, max_fps: int = 60):
        super().__init__(name, parent)

        self.type = "no_loop"

        self.register_to_driver("camera", "color")

        self.create_event("faces_landmarks")

        self.debug_time = False
        self.debug_data = False
        self.fps = max_fps
        self.window = 1

    def pre_run(self):
        """Runs once at the start of the driver"""
        super().pre_run()

        self.landmarker = fpe.init()
        self.create_callback_on_event("estimate_face_pose", self.estimate_face_pose, "camera", "color")


    def estimate_face_pose(self, camera_color_frame):
        """Runs face pose estimation on camera frame"""

        if camera_color_frame is not None:
            face_pose_data = fpe.estimate(self.landmarker, camera_color_frame, self.window)
            self.set_event_data("faces_landmarks", face_pose_data)
