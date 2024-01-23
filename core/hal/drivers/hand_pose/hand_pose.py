# Hand Pose estimation Driver

import time

import numpy as np

import core.hal.drivers.hand_pose.utils.hand_pose_estimation as hpe
from core.hal.drivers.driver import BaseDriver


class Driver(BaseDriver):
    """Hand pose driver"""
    def __init__(self, name: str, parent, max_fps: int = 60):
        super().__init__(name, parent)

        self.type = "no_loop"

        self.register_to_driver("camera", "color")

        self.create_event("raw_data")

        self.debug_time = False
        self.debug_data = False
        self.fps = max_fps
        self.window = 1

    def pre_run(self):
        """Runs once at the start of the driver"""
        super().pre_run()

        self.hands = hpe.init()
        self.create_callback_on_event("evaluate_pose", self.eval_on_frame, "camera", "color")


    def eval_on_frame(self, data, marker=None):
        """Runs hand pose estimation on frame"""
        start_t = time.time()

        color = data

        if color is not None:
            raw_data = hpe.find_all_hands(self.hands, color, self.window)

            flag_1 = time.time()

            self.log(raw_data, 3)
            self.set_event_data("raw_data", raw_data)

            if self.debug_data:
                self.log(raw_data)

            if self.debug_time:
                self.log(f"Inference: {(flag_1 - start_t)*1000} ms")
                # self.log(f"Data: {(flag_1 - start_t)*1000} ms")

        end_t = time.time()

        if self.debug_time:
            self.log(f"Total time: {(end_t - start_t)*1000}ms")
            self.log(f"FPS: {int(1/(end_t - start_t))}")

        # dt = max((1 / self.fps) - (end_t - start_t), 0.0001)
        # time.sleep(dt)
