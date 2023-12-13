import base64
import cv2
import io
import numpy as np
import onnxruntime
from PIL import Image

from core.hal.drivers.driver import BaseDriver

class Driver(BaseDriver):
    """
    Paintstorch driver
    Colorizes a sketch with strokes only in the focus area
    """

    def __init__(
        self, name: str, parent
    ):
        super().__init__(name, parent)

        self.type = "no_loop"

        self.register_to_driver("camera", "color")
        self.register_to_driver("calibration", "successful_calibration_data")
        self.create_event("painted_image")

    def pre_run(self):
        super().pre_run()

        self.model = onnxruntime.InferenceSession("core/hal/drivers/paintstorch/model.onnx")
        self.create_callback("paint_image", self.paint_image)

    def paint_image(self, data):
        """
        data; dict
            {
                "drawing_coords": list of tuples
                    The coordinates of the drawing
                "screen_size": tuple
                    The size of the screen
                "hints": array
                    The hints image
            }
        """
        color = self.parent.get_driver_event_data("camera", "color")
        calibration_data = self.parent.get_driver_event_data("calibration", "successful_calibration_data")


        if color is None:
            return

        drawing_coords = data["drawing_coords"]
        canvas_coords = data["canvas_coords"]
        width, height = data["screen_size"]
        hints = data["hints"].split(",")[1]
        base64_decoded = base64.b64decode(hints)
        hints = Image.open(io.BytesIO(base64_decoded))
        hints = np.array(hints)

        if calibration_data is None:
            return

        camera_to_display_matrix = np.array(calibration_data["camera_to_display_matrix"])
        display_to_camera_matrix = np.array(calibration_data["display_to_camera_matrix"])
        display_to_canvas_matrix = cv2.findHomography(np.float32([[0, 0], [width, 0], [width, height], [0, height]]), np.float32(canvas_coords))[0]
        # camera_to_focus_matrix = np.matmul(camera_to_display_matrix, display_to_focus_matrix)


        drawing_camera_coords = [
            [
                x * display_to_camera_matrix[0][0] + y * display_to_camera_matrix[0][1] + display_to_camera_matrix[0][2],
                x * display_to_camera_matrix[1][0] + y * display_to_camera_matrix[1][1] + display_to_camera_matrix[1][2],
            ] for x, y in drawing_coords
        ]

        drawing_transform = cv2.getPerspectiveTransform(np.float32(drawing_camera_coords), np.float32([[0, 0], [512, 0], [512, 512], [0, 512]]))
        x = cv2.warpPerspective(color, drawing_transform, (512, 512), flags=cv2.INTER_LINEAR)

        hints_canvas_coords = [
            [
                x - canvas_coords[0][0],
                y - canvas_coords[0][1],
            ] for x, y in drawing_coords
        ]
        hints_transform = cv2.getPerspectiveTransform(np.float32(hints_canvas_coords), np.float32([[0, 0], [128, 0], [128, 128], [0, 128]]))
        h = cv2.warpPerspective(hints, hints_transform, (128, 128), flags=cv2.INTER_LINEAR)

        # print(x.shape)
        # print(h.shape)

        # Convert x to black and white
        x = cv2.cvtColor(x, cv2.COLOR_BGR2GRAY)
        x = cv2.threshold(x,127, 255, cv2.THRESH_BINARY)[1]
        x = cv2.cvtColor(x, cv2.COLOR_GRAY2BGR)

        Image.fromarray(x).save("x_onnxruntime.png")
        Image.fromarray(h).save("h_onnxruntime.png")

        x = x / 255
        h = h / 255

        m = np.ones((512, 512))
        x = np.concatenate([x, m[:, :, None]], axis=-1)

        x[:, :, :3] = (x[:, :, :3] - 0.5) / 0.5
        h[:, :, :3] = (h[:, :, :3] - 0.5) / 0.5

        x = np.array(x, dtype=np.float32)
        h = np.array(h, dtype=np.float32)

        x = x.transpose((2, 0, 1)).reshape((1, 4, 512, 512))
        h = h.transpose((2, 0, 1)).reshape((1, 4, 128, 128))

        res = self.model.run(None, {"input": x, "hints": h})

        y = res[0][0].transpose((1, 2, 0))
        y = ((y * 0.5 + 0.5) * 255).astype(np.uint8)

        Image.fromarray(y).save("y_onnxruntime.png")
