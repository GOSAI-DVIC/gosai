# Balls estimation Driver
# Return a list containing x,y ball positions

from __future__ import annotations
from core.hal.drivers.driver import BaseDriver
from dataclasses import dataclass
from typing import Any

import cv2
import json
import numpy as np
import time


DEFAULT_MIN_SLEEP = 1e-4  # In seconds ~ 0.1ms

DEFAULT_JSON_PATH = "home/calibration_data.json"
DEFAULT_BKG_PATH = "home/background.jpg"

DEFAULT_SIZE = 1920, 1080
DEFAULT_MIN_MOMENT_00 = np.pi * 15 ** 2
DEFAULT_MIN_DISTANCE = 10


@dataclass
class Camera:
    projection_matrix: np.ndarray
    pool_focus_matrix: np.ndarray

    def warp_projection(self, img: np.ndarray, size: tuple(int, int)) -> np.ndarray:
        blue_chan = img[..., -1]
        return cv2.warpPerspective(blue_chan, self.pool_focus_matrix, size, flags=cv2.INTER_LINEAR)

    def project(self, point: np.ndarray) -> np.ndarray:
        # point = self.projection_matrix @ point
        # point = point / point[-1]
        
        return point

    @classmethod
    def from_dict(cls, data: dict(str, Any)) -> "Camera":
        projection_matrix = np.array(data["projection_matrix"])
        poolFocus_matrix = np.array(data["poolFocus_matrix"])
        return cls(projection_matrix, poolFocus_matrix)

def detect_balls(bkg: np.ndarray, frame: np.ndarray, camera: Camera) -> list(tuple(int, int)):
    # cv2.imwrite("home/bkg.jpg", bkg)
    # cv2.imwrite("home/frame.jpg", frame)
    frame = cv2.absdiff(bkg, frame)
    # cv2.imwrite("home/absdiff.jpg", frame)
    frame = camera.warp_projection(frame, DEFAULT_SIZE)
    # cv2.imwrite("home/warped.jpg", frame) #check calibration_data.json if looks wrong
    frame = cv2.GaussianBlur(frame, (5, 5), 0)
    _, frame = cv2.threshold(frame, 100, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    moments = list(map(cv2.moments, contours))

    balls = []
    for contour, moment in zip(contours, moments):
        if moment["m00"] < DEFAULT_MIN_MOMENT_00:
            continue

        contour = np.array(contour)[:, 0, :]
        position = np.array([
            int(moment["m10"] / moment["m00"]),
            int(moment["m01"] / moment["m00"]),
            1,
        ])

        distances = np.sqrt(((position[None, :2] - contour) ** 2).sum(axis=1))
        if np.std(distances) < DEFAULT_MIN_DISTANCE:
            # x, y, _ = camera.project(position)
            x, y, _ = position[0], position[1], 0 #- 960, position[1] - 540, 0
            balls.append((int(x), int(y)))

    return balls


@dataclass
class RuningMean:
    value: float
    step: int

    def update(self, value: float) -> float:
        self.value = self.value * self.step + value
        self.step += 1
        self.value = self.value / self.step
        return self.value


class Driver(BaseDriver):
    def __init__(self, name: str, parent, max_fps: int = 120) -> None:
        super().__init__(name, parent)

        self.register_to_driver("camera", "color")
        self.create_event("balls")
        self.create_event("fps")

        self.fps = max_fps
        self.stable_fps = RuningMean(60, 1)
        self.history = []

    def pre_run(self) -> None:
        super().pre_run()

        with open(DEFAULT_JSON_PATH, 'r') as f:
            data = json.load(f)

        self.bkg = cv2.imread(DEFAULT_BKG_PATH)
        self.camera = Camera.from_dict(data)

    def loop(self) -> None:
        start_t = time.time()

        frame = self.parent.get_driver_event_data("camera", "color")
        if frame is not None:
            if self.bkg.shape != frame.shape:
                self.bkg = cv2.resize(self.bkg, (frame.shape[1], frame.shape[0]))
            balls = detect_balls(self.bkg, frame, self.camera)

            # print(balls)
            self.set_event_data("balls", balls)

        dt = time.time() - start_t
        time.sleep(max(1 / self.fps - dt, DEFAULT_MIN_SLEEP))

        dt = time.time() - start_t
        # fps = self.stable_fps.update(1 / dt)
        fps = 1 / dt
        if len(self.history) < 50:
            self.history.append(fps)
        else:
            self.history.pop(0)
            self.history.append(fps)

        self.set_event_data("fps", f"{np.mean(self.history):.2f}")
