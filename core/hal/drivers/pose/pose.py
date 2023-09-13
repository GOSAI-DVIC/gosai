# Pose estimation Driver

import time
import numpy as np
import core.hal.drivers.pose.utils.pose_estimation as pe
from core.hal.drivers.driver import BaseDriver
from os import path
import json


class Driver(BaseDriver):
    """
    * Body pose from mediapipe
    ! Only one instance from mediapipe can run
    """

    def __init__(self, name: str, parent, max_fps: int = 60):
        super().__init__(name, parent)

        self.register_to_driver("camera", "color")

        self.create_event("raw_data")

        self.debug_time = False
        self.debug_data = False
        self.fps = max_fps
        self.window = 1.0
        if path.exists("home/config.json"):
            with open("home/config.json", "r") as f:
                config = json.load(f)
                if "screen" in config:
                    if ("window" in config["screen"]):
                        self.window = config["screen"]["window"]

    def pre_run(self):
        super().pre_run()

        self.holistic = pe.init()

    def loop(self):
        start_t = time.time()

        color = self.parent.get_driver_event_data("camera", "color")

        if color is not None:
            raw_data = pe.find_all_poses(self.holistic, color, self.window)

            flag_1 = time.time()
            self.set_event_data("raw_data", raw_data)

            if self.debug_data:
                self.log(raw_data)

            if self.debug_time:
                self.log(f"Inference: {(flag_1 - start_t)*1000} ms")

        else:
            self.log("No color data", 1)

        end_t = time.time()

        if self.debug_time:
            self.log(f"Total time: {(end_t - start_t)*1000}ms")
            self.log(f"FPS: {int(1/(end_t - start_t))}")

        # dt = max((1 / self.fps) - (end_t - start_t), 0.0001)

        # time.sleep(dt)
