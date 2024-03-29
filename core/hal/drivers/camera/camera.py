# Video driver
import json
import os
import sys
import time
from os import path

from core.hal.drivers.camera.configs import IntelCamera, StandardCamera
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

    def pre_run(self):
        super().pre_run()

        config = self.parent.config
        if (
            "type" in config["camera"]
            and "width" in config["camera"]
            and "height" in config["camera"]
        ):
            if config["camera"]["type"] == "standard":
                self.source = StandardCamera(
                    config["camera"]["width"], config["camera"]["height"], config["camera"]["number"]
                ) if "number" in config["camera"] else StandardCamera(
                    config["camera"]["width"], config["camera"]["height"]
                )
            elif config["camera"]["type"] == "intel":

                self.source = IntelCamera(
                    config["camera"]["width"], config["camera"]["height"]
                ) if "number" in config["camera"] else IntelCamera(
                    config["camera"]["width"], config["camera"]["height"]
                )
        else:
            self.source = StandardCamera(1920, 1080, 0)

    def loop(self):
        # print(self.source)
        self.color, self.depth = self.source.next_frame()

        if self.color is not None:
            self.set_event_data("color", self.color)
        if self.depth is not None:
            self.set_event_data("depth", self.depth)

        # time.sleep(1 / self.fps)  # Runs faster to be sure to get the current frame

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
