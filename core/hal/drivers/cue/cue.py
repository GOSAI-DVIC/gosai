# cues estimation Driver
# Return a list containing x,y cue positions

import time

import core.hal.drivers.cue.utils.cue_detection as cd
from core.hal.drivers.driver import BaseDriver

class Driver(BaseDriver):

    def __init__(self, name: str, parent, max_fps: int = 120):
        super().__init__(name, parent)

        self.paused = False

        self.register_to_driver("video", "color")

        self.create_event("cue_data")

        self.fps = max_fps

    def pre_run(self):
        super().pre_run()

        self.camera_data, self.empty_bg = cd.init()

    def loop(self):
        start_t = time.time()
        color = self.parent.get_driver_event_data("video","color")
        if color is not None:
            cue_data = cd.CueDetection(
                self.empty_bg,
                color, #to get a frame
                self.camera_data
            ) #it returns l
            self.set_event_data("cue_data",cue_data)

        dt = max(1 / self.fps - (time.time() - start_t), 0.0001)
        time.sleep(dt)
