# Pose estimation Driver

import os
import sys
import time
import numpy as np
import core.hal.drivers.slr.utils.get_sign as gs
from core.hal.drivers.driver import BaseDriver


class Driver(BaseDriver):
    """Sign Language Recognition driver"""

    def __init__(self, name: str, parent):
        super().__init__(name, parent)

        self.register_to_driver("pose", "raw_data")
        self.create_event("new_sign")

        self.SLR_ACTIONS = [
            "nothing",
            "empty",
            "hello",
            "thanks",
            "iloveyou",
            # "what's up",
            # "hey",
            # "my",
            # "name",
            # "nice",
            # "to meet you",
        ]

        self.model = gs.init(len(self.SLR_ACTIONS))
        self.frames = []
        self.fps = 30
        # self.timeloop_start = 0
        self.update_time = 0
        self.count_update = 0

    def loop(self):
        start_t = time.time()

        #frame = bytes_to_dict(self.parent.get_driver_event_data("pose", "raw_data"))
        frame = self.parent.get_driver_event_data("pose", "raw_data")
        if frame is not None:
            if self.frames:
                if list(frame) != list(self.frames)[-1]:
                    if len(self.frames) < 30:
                        self.frames.append(gs.adapt_data(frame))
                        self.count_update +=1

                    elif len(self.frames) == 30:
                        self.frames.append(gs.adapt_data(frame))
                        self.count_update +=1

                        # timeloop = time.time()-self.timeloop_start
                        # while(timeloop < 0.09):
                        #     timeloop = time.time()-self.timeloop_start
                        # self.timeloop_start = time.time()
                        #print("TIMELOOP", timeloop)

                        self.frames = self.frames[-30:]
                        guessed_sign, probability = gs.get_sign(
                                self.model, self.frames, self.SLR_ACTIONS)
                        if(self.count_update >= 60):
                            self.count_update = 0

                            #print("waiting : ", time.time() - self.update_time)
                            #print("proba * 2000 ", probability*2000)
                            #if(time.time() - self.update_time > probability*2000):

                            guessed_sign, probability = gs.get_sign(
                                self.model, self.frames, self.SLR_ACTIONS)

                        print(guessed_sign)
                        self.set_event_data(
                            "new_sign", {"guessed_sign": guessed_sign, "probability": probability, "actions": self.SLR_ACTIONS}
                        )
                        #self.update_time = time.time()
                        
            else:
                self.frames.append(gs.adapt_data(frame))

        end_t = time.time()

        dt = max((1 / self.fps) - (end_t - start_t), 0.0001)

        time.sleep(dt)
