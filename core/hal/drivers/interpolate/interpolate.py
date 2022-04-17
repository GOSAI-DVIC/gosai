import time

from core.hal.drivers.driver import BaseDriver


class Driver(BaseDriver):
    """
    Interpolates any data a certain amount of time for a given duration
    """

    def __init__(self, name: str, parent):
        super().__init__(name, parent)

        self.type = "no_loop"

        self.create_event("interpolated_data")
        self.create_callback("interpolate_points", self.interpolate_points)

        self.prev_points = {}

    def interpolate_points(self, data):
        """
        Interpolate points at a given rate for a given amount of time
        """
        name = data["name"]
        amount = data["amount"]
        duration = data["duration"]
        points = data["points"]
        factor = data["factor"]
        depth = data["depth"]

        exec_time = 0
        for _ in range(amount - 1):
            start_time = time.time()
            points = interpolate(
                self.prev_points.get(name, None), points, factor, depth
            )
            self.prev_points[name] = points
            self.set_event_data("interpolated_data", {"name": name, "points": points})
            exec_time += time.time() - start_time
            time.sleep(max((duration / amount) - (time.time() - start_time), 0))


        start_time = time.time()
        points = interpolate(self.prev_points.get(name, None), points, factor, depth)
        self.prev_points[name] = points
        self.set_event_data("interpolated_data", {"name": name, "points": points})
        exec_time += time.time() - start_time
        return exec_time * 1000

def interpolate(prev_points: list, points: list, factor: float, depth: int = 2) -> list:
    """
    Interpolate points at a given rate for a given amount of time
    """
    if prev_points is None or not same_dimension(prev_points, points):
        return points

    if points == []:
        return prev_points

    if depth == 0:
        return lerp(prev_points[:2], points[:2], factor) + points[2:]

    else:
        return [
            interpolate(prev_points[i], points[i], factor, depth - 1)
            for i in range(len(prev_points))
        ]


def lerp(p1: list, p2: list, t: float) -> list:
    """
    Linear interpolation
    """
    return [p1[0] + (p2[0] - p1[0]) * t, p1[1] + (p2[1] - p1[1]) * t]


def same_dimension(l1: list, l2: list) -> bool:
    """
    Check if two lists have the same dimension
    """
    if type(l1) != type(l2):
        return False
    if type(l1) == list:
        return len(l1) == len(l2) and (len(l1) == 0 or same_dimension(l1[0], l2[0]))
    return True
