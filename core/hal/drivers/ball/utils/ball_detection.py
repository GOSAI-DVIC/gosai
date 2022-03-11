from turtle import pos
import numpy as np
import cv2
import json

def init(filename_bg = "background.jpg"):
    with open('home/calibration/calibration_data.json', 'r') as f:
        data = json.load(f)
    bkg = cv2.imread(f"core/hal/drivers/ball/utils/{filename_bg}")
    return data, bkg

def ImageProcessing(img, camera_data): #Process a frame : gray scale + warpPerspective
    img = img[:,:,2]
    img = cv2.warpPerspective(img, np.array(camera_data["poolFocus_matrix"]), (1920, 1080), flags=cv2.INTER_LINEAR)
    return img

# def ball_dectection(empty: np.ndarray, frame: np.ndarray, cam2screen: np.ndarray) -> np.ndarray:
#     """Ball Detection
    
#     Detect pool balls in screen coords and then project their position into projector coords

#     Parameters
#     ----------
#     empty: np.ndarray
#         reference empty background to perform frame difference

#     frame: np.ndarray
#         current frame from camera

#     cam2screen: np.ndarray
#         camera to screen projection matrix

#     Returns
#     -------
#     balls: np.ndarray
#         detected ball projector coords
#     """
#     return None

# from dataclasses import dataclass

# import json


# @dataclass
# class CameraData:
#     projection_matrix:  np.ndarray
#     poolFocus_matrix: np.ndarray
#     detected_coords: np.ndarray
#     pool_coords: np.ndarray
#     screen_coords: np.ndarray
#
#     @classmethod
#     def from_dict(cls, path: str) -> "CameraData":
#         with open(path, "r") as fp:
#             data = json.load(fp)
#         return cls(**{k: np.ndarray(v) for k, v in data.items()})


# camdata = CameraData.from_dict("pathtosjon.json")
# camdata.projection_matrix


def BallDetection(bkg, frame, camera_data):
    matrix = np.array(camera_data["projection_matrix"])
    inv_matrix = np.linalg.inv(matrix)

    frame = cv2.absdiff(bkg, frame)
    frame = ImageProcessing(frame, camera_data)
    frame = cv2.GaussianBlur(frame, (5, 5), 0)
    _, frame = cv2.threshold(frame, 100, 255, cv2.THRESH_BINARY)

    contours, _ = cv2.findContours(frame, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    moments = map(cv2.moments, contours)

    balls = [(i * 1080, j * 1920) for i in range(2) for j in range(2)]
    for contour, moment in zip(contours, moments):
        if moment["m00"] < np.pi * 15 ** 2:
            continue

        contour = np.array(contour)[:, 0, :]
        position = np.array([
            int(moment["m10"] / moment["m00"]),
            int(moment["m01"] / moment["m00"]),
            1,
        ])

        widths = np.sqrt(((position[None, :2] - contour) ** 2).sum(axis=1))
        if np.std(widths) < 10:
            x_, y_, _ = position
            d = inv_matrix[2, 0] * x_ + inv_matrix[2, 1] * y_ + inv_matrix[2, 2]
            x = inv_matrix[0, 0] * x_ + inv_matrix[0, 1] * y_ + inv_matrix[0, 2] / d
            y = inv_matrix[1, 0] * x_ + inv_matrix[1, 1] * y_ + inv_matrix[1, 2] / d

            # position = inv_matrix @ position
            # position = matrix @ position
            # x, y, z = position
            
            balls.append((int(x), int(y)))

    return balls

def is_null(matrix: np.ndarray) -> bool:
    return (matrix == 0).sum() > 0