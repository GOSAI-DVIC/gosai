# Pose estimation Driver

import os
import sys
import time
import numpy as np
import core.hal.drivers.slr.utils.get_sign as gs
from core.hal.drivers.driver import BaseDriver
import onnxruntime
import onnxruntime as ort


class Driver(BaseDriver):
    """Sign Language Recognition driver for the sign language training"""

    def __init__(self, name: str, parent):
        super().__init__(name, parent)

        self.register_to_driver("pose", "raw_data")
        self.create_event("new_sign")
        self.SLR_ACTIONS = []

        self.model = None
        self.frames = []
        self.fps = 30
        self.update_time = 0
        self.count_update = 0

    def pre_run(self):
        self.create_callback("set_actions", self.set_actions)

    def set_actions(self, actions):
        self.SLR_ACTIONS = actions
        self.model = gs.init(len(self.SLR_ACTIONS))

    def loop(self):
        start_t = time.time()

        frame = self.parent.get_driver_event_data("pose", "raw_data")
        if frame is not None and self.model is not None:
            if self.frames:
                if list(frame) != list(self.frames)[-1]:
                    if len(self.frames) < 30:
                        self.frames.append(gs.adapt_data(frame))
                        self.count_update +=1

                    elif len(self.frames) == 30:
                        self.frames.append(gs.adapt_data(frame))
                        self.count_update +=1

                        self.frames = self.frames[-30:]
                        guessed_sign, probability = gs.get_sign(
                                self.model, self.frames, self.SLR_ACTIONS)
                        if(self.count_update >= 60):
                            self.count_update = 0

                            guessed_sign, probability = gs.get_sign(
                                self.model, self.frames, self.SLR_ACTIONS)

                        self.set_event_data(
                            "new_sign", {"guessed_sign": guessed_sign, "probability": probability}
                        )
                        
            else:
                self.frames.append(gs.adapt_data(frame))

        end_t = time.time()

        dt = max((1 / self.fps) - (end_t - start_t), 0.0001)

        time.sleep(dt)


