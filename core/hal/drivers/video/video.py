# Video driver

import os
import sys
import time

from core.hal.drivers.video.cameras import IntelCamera, StandardCamera
from core.hal.drivers.driver import BaseDriver


class Driver(BaseDriver):
    """
    (Thread)
    * Reads frames using the source
    * and stores them into global variables. depth will be none if
    * the camera isn't the Intel D435
    """

    def __init__(
        self, name: str, parent, fps: int = 30
    ):  # TODO: Create Camera object and inherit the others from it
        super().__init__(name, parent)

        self.fps = fps

        self.create_event("color")
        self.create_event("depth")
        self.create_event("source")

    def pre_run(self):
        self.source = IntelCamera(640, 480)

    def loop(self):
        # print(self.source)
        color, depth = self.source.next_frame()

        if color is not None:
            self.set_event_data("color", color)
        if depth is not None:
            self.set_event_data("depth", depth)

        time.sleep(1 / self.fps)  # Runs faster to be sure to get the current frame

    def execute(self, command, arguments=""):
        super().execute(command, arguments)

        if command == "get":
            if arguments == "color":
                return self.color
            elif arguments == "depth":
                return self.depth
            else:
                self.log(f"Unknown argument: {arguments}", 3)
                return -1
        else:
            self.log(f"Unknown command: {command}", 3)
            return -1
