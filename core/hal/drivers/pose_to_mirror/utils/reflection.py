import math
from typing import List

import numpy as np
import pyrealsense2 as rs

theta = math.radians(17)
color_intrinsics = None
depth_intrinsics = None


def get_depth(point: list, depth_frame, depth_radius: int) -> float:
    """Gets the depth of a pixel using the points around it"""
    x = min(max(int(point[0]), 0), len(depth_frame[0]))
    y = min(max(int(point[1]), 0), len(depth_frame))

    try:
        return np.float64(
            np.min(
                depth_frame[
                    max(y - depth_radius, 0) : min(y + depth_radius, len(depth_frame)),
                    max(x - depth_radius, 0) : min(
                        x + depth_radius, len(depth_frame[0])
                    ),
                ]
            )
        )
    except:
        return np.float64(depth_frame[x, y])


def map_location(
    point: list,
    eyes_depth: int,
    eyes_coordinates: list,
    point_depth: int,
    video_provider,
) -> List[int]:
    """Transforms pixel to world coordinates"""
    da = eyes_depth
    db = point_depth
    xa, ya, za = eyes_coordinates

    xb, yb, zb = rs.rs2_deproject_pixel_to_point(color_intrinsics, point, db)

    ya = ya * math.cos(theta) + za * math.sin(theta)
    yb = yb * math.cos(theta) + zb * math.sin(theta)

    dz = db + da
    dy = yb - ya
    dx = xb - xa
    if dz != 0:
        yi = ya + (da / dz) * dy
        xi = xa + (da / dz) * dx
        if not math.isnan(xi) and not math.isnan(yi):
            return [int(xi), int(yi)]

    return [-1, -1]


def project(
    points: List[List],
    eyes_position: list,
    video_provider,
    depth_frame,
    depth_radius,
    ref=0,
) -> List[List]:
    """Projects every keypoint in world coordinates based on the user's point of view"""
    global color_intrinsics, depth_intrinsics

    if color_intrinsics is None:
        color_intrinsics = create_intrinsics(video_provider["color_intrinsics"])

    if depth_intrinsics is None:
        depth_intrinsics = create_intrinsics(video_provider["depth_intrinsics"])

    projected = []
    eyes_depth = get_depth(eyes_position, depth_frame, 4)  # Depth of the eye
    eyes_coordinates = rs.rs2_deproject_pixel_to_point(
        depth_intrinsics, eyes_position, eyes_depth
    )

    for point in points:
        if bool(point):
            visibility = point[2] if ref == 0 else ref[3]
            point_depth = (
                get_depth(point[0:2], depth_frame, depth_radius) if ref == 0 else ref[2]
            )  # Depth of the point
            projected.append(
                map_location(
                    point=point[0:2],
                    eyes_depth=eyes_depth,
                    eyes_coordinates=eyes_coordinates,
                    point_depth=point_depth,
                    video_provider=video_provider,
                )
                + [int(point_depth)]
                + [visibility]
            )
    return projected


def create_intrinsics(params: dict):
    intrinsic = rs.pyrealsense2.intrinsics()
    intrinsic.width = params["width"]
    intrinsic.height = params["height"]
    intrinsic.ppx = params["ppx"]
    intrinsic.ppy = params["ppy"]
    intrinsic.fx = params["fx"]
    intrinsic.fy = params["fy"]
    intrinsic.model = params["model"]
    intrinsic.coeffs = params["coeffs"]
    return intrinsic
