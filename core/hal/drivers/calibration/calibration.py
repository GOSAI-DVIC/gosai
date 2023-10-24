import numpy as np

from core.hal.drivers.driver import BaseDriver
from core.hal.drivers.calibration.utils.matrix_from_aruco import get_display_camera_projection_matrix, get_display_focus_projection_matrix

class Driver(BaseDriver):
    """
    Calibration driver
    Provides matrix to transform camera points to display points and display points to focus area points
    """

    def __init__(
        self, name: str, parent
    ):
        super().__init__(name, parent)

        self.register_to_driver("camera", "color")
        self.create_event("calibration_data")

    def pre_run(self):
        super().pre_run()

        self.create_callback("calibrate_camera_display", self.calibrate_camera_display)
        self.create_callback("calibrate_display_focus", self.calibrate_display_focus)

    def calibrate_camera_display(self, data):
        """
        Get the matrix to transform a camera point to a display point and vice versa.

        Must be called from an app displaying the aruco markers on the display.
        """
        color = self.parent.get_driver_event_data("camera", "color")
        original_data = self.parent.get_driver_event_data("calibration", "calibration_data")

        if original_data is None:
            original_data = {}

        if color is None:
            return

        data = get_display_camera_projection_matrix(color, aruco_display_coords=data)

        if "display_to_focus_matrix" in original_data and len(original_data["display_to_focus_matrix"]) > 0 and len(data["camera_to_display_matrix"]) > 0:
            data["camera_to_focus_matrix"] = np.matmul(np.array(data["camera_to_display_matrix"]), np.array(original_data["display_to_focus_matrix"])).tolist()
            data["focus_to_camera_matrix"] = np.matmul(np.array(original_data["focus_to_display_matrix"]), np.array(data["display_to_camera_matrix"])).tolist()

        original_data.update(data)

        self.set_event_data("calibration_data", original_data)

    def calibrate_display_focus(self, data):
        """Get the matrix to transform a display point to a focus area point and vice versa"""
        original_data = self.parent.get_driver_event_data("calibration", "calibration_data")

        if original_data is None:
            original_data = {}

        display_coords = data["display_coords"]
        focus_coords = data["focus_coords"]

        data = get_display_focus_projection_matrix(display_coords=display_coords, focus_coords=focus_coords)

        if "camera_to_display_matrix" in original_data and len(original_data["camera_to_display_matrix"]) > 0 and len(data["display_to_focus_matrix"]) > 0:
            data["camera_to_focus_matrix"] = np.matmul(np.array(original_data["camera_to_display_matrix"]), np.array(data["display_to_focus_matrix"])).tolist()
            data["focus_to_camera_matrix"] = np.matmul(np.array(data["focus_to_display_matrix"]), np.array(original_data["display_to_camera_matrix"])).tolist()

        original_data.update(data)

        self.set_event_data("calibration_data", original_data)
