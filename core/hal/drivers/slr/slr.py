# Pose estimation Driver

import os
import sys
import time

import core.hal.drivers.slr.utils.get_sign as gs
from core.hal.drivers.driver import BaseDriver
from core.tools.binary_conversions import dict_to_bytes, bytes_to_dict

class Driver(BaseDriver):
    """Sign Language Recognition driver"""

    def __init__(self, name: str, parent):
        super().__init__(name, parent)

        self.register_to_driver("pose", "raw_data")
        self.create_event("new_sign")

        self.model = gs.init()
        self.frames = []
        self.fps = 60

    def loop(self):
        start_t = time.time()

        frame = bytes_to_dict(self.parent.get_driver_event_data("pose", "raw_data"))

        if frame is not None:

            if len(self.frames) < 30:
                self.frames.append(frame)

            elif len(self.frames) == 30:
                self.frames.pop(0)
                self.frames.append(frame)
                sign, probability = gs.get_sign(self.model, self.frames)
                self.set_event_data(
                    "new_sign", dict_to_bytes({"sign": sign, "probability": probability})
                )
                #(sign," ", probability)

        end_t = time.time()

        dt = max((1 / self.fps) - (end_t - start_t), 0.0001)

        time.sleep(dt)
