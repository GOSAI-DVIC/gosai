# Hand Pose estimation Driver

import time

import core.hal.drivers.hand_sign.utils.hand_recognition as hs
from core.hal.drivers.driver import BaseDriver


class Driver(BaseDriver):
    """Hand pose driver"""
    def __init__(self, name: str, parent, max_fps: int = 60):
        super().__init__(name, parent)

        self.type = "no_loop"

        self.register_to_driver("hand_pose", "raw_data")

        self.create_event("sign")

        self.debug_time = False
        self.debug_data = False
        self.fps = max_fps

    def pre_run(self):
        """Runs once at the start of the driver"""
        super().pre_run()

        self.sign_provider = hs.init()
        self.create_callback_on_event("detect", self.eval_on_frame, "hand_pose", "raw_data")


    def eval_on_frame(self, data):
        """Runs sign detection on frame"""
        start_t = time.time()

        hand_pose = data["hands_landmarks"]

        if hand_pose is not None:
            hand_sign = [hs.find_gesture(self.sign_provider, pose) for pose in hand_pose]

            flag_1 = time.time()
            self.set_event_data("sign", hand_sign)

            if self.debug_data:
                self.log(hand_sign)

            if self.debug_time:
                self.log(f"Inference: {(flag_1 - start_t)*1000} ms")
                # self.log(f"Data: {(flag_1 - start_t)*1000} ms")

        else:
            self.log("No color data", 1)

        end_t = time.time()

        if self.debug_time:
            self.log(f"Total time: {(end_t - start_t)*1000}ms")
            self.log(f"FPS: {int(1/(end_t - start_t))}")

        # dt = max((1 / self.fps) - (end_t - start_t), 0.0001)
        # time.sleep(dt)
