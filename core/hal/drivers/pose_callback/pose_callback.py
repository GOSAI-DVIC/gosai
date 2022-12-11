# Pose estimation Driver
import codecs
from io import BytesIO
from PIL import Image
import base64
import time
import numpy as np
import core.hal.drivers.pose_callback.utils.pose_estimation as pe
from core.hal.drivers.driver import BaseDriver
from os import path
import json
import cv2


class Driver(BaseDriver):
    """
    * Body pose from mediapipe
    ! Only one instance from mediapipe can run
    """

    def __init__(self, name: str, parent, max_fps: int = 60):
        super().__init__(name, parent)
        # self.type = "no_loop"

        self.create_event("raw_data")
        self.create_callback("estimate_pose", self.estimate_pose)

        self.__holistic = None

        self.debug_time = False
        self.debug_data = False
        self.fps = max_fps
        if path.exists("home/config.json"):
            with open("home/config.json", "r") as f:
                config = json.load(f)
                if ("window" in config["screen"]): 
                    self.window = config["screen"]["window"]
                else :
                    self.window = 1.0

    def pre_run(self):
        super().pre_run()
        self.__holistic = pe.init()

    def estimate_pose(self, base64_color):
        start_t = time.time()
        # color = self.parent.get_driver_event_data("camera", "color")
        if self.__holistic is None:
            self.__holistic = pe.init()
        else:
            if base64_color is not None:
                # color = np.array(Image.open(BytesIO(base64.decodebytes(bytes(base64_color, "utf-8")))))
                color = cv2.cvtColor(np.array(Image.open(BytesIO(base64.b64decode(base64_color)))), cv2.COLOR_BGR2RGB) 
                raw_data = pe.find_all_poses(self.__holistic, color, self.window)
                self.set_event_data("raw_data", raw_data)

                raw_data_cables = pe.find_all_poses_cables(self.__holistic, color)
                self.set_event_data("raw_data_cables", raw_data_cables)
                
            else:
                self.log("No color data", 1)

            end_t = time.time()

            if self.debug_time:
                self.log(f"Total time: {(end_t - start_t)*1000}ms")
                self.log(f"FPS: {int(1/(end_t - start_t))}")

            # dt = max((1 / self.fps) - (end_t - start_t), 0.0001)

            # time.sleep(dt)
