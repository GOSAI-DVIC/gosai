import cv2 as cv
import numpy as np


class StandardCamera:
    """
    * A class that reads frames from the webcam (color only)
    """

    def __init__(self, width, height, id: int = 0):
        self.name = "basic"
        self.width = width
        self.height = height
        self.cap = cv.VideoCapture(id)
        self.cap.set(3, self.width)
        self.cap.set(4, self.height)

    def next_frame(self):
        """Collects color frames"""

        _, frame = self.cap.read()
        return [frame, None]


class IntelCamera:
    """
    * Reads frames from the intel Realsense D435I Camera (color and depth frames)
    """

    def __init__(self, width, height):
        self.name = "d435"
        import pyrealsense2 as rs

        self.pipe = rs.pipeline()
        config = rs.config()

        self.width = width
        self.height = height

        config.enable_stream(
            rs.stream.depth, self.width, self.height, rs.format.z16, 30
        )
        config.enable_stream(
            rs.stream.color, self.width, self.height, rs.format.bgr8, 30
        )

        profile = self.pipe.start(config)

        depth_sensor = profile.get_device().first_depth_sensor()
        self.depth_scale = depth_sensor.get_depth_scale()

        clipping_distance_in_meters = 3
        clipping_distance = clipping_distance_in_meters / self.depth_scale

        self.depth_intrinsics = profile.get_stream(rs.stream.depth).as_video_stream_profile().get_intrinsics()
        self.color_intrinsics = profile.get_stream(rs.stream.color).as_video_stream_profile().get_intrinsics()

        align_to = rs.stream.color
        self.align = rs.align(align_to)

        self.depth_to_disparity = rs.disparity_transform(True)
        self.disparity_to_depth = rs.disparity_transform(False)
        self.dec_filter = rs.decimation_filter()
        self.temp_filter = rs.temporal_filter()
        self.spat_filter = rs.spatial_filter()

    def next_frame(self):
        """Collects color and frames"""
        frameset = self.pipe.wait_for_frames()

        aligned_frames = self.align.process(frameset)

        color_frame = aligned_frames.get_color_frame()
        depth_frame = aligned_frames.get_depth_frame()

        # self.depth_intrinsics = depth_frame.profile.as_video_stream_profile().intrinsics
        # self.color_intrinsics = color_frame.profile.as_video_stream_profile().intrinsics

        depth_frame = self.depth_to_disparity.process(depth_frame)
        depth_frame = self.dec_filter.process(depth_frame)
        depth_frame = self.temp_filter.process(depth_frame)
        depth_frame = self.spat_filter.process(depth_frame)
        depth_frame = self.disparity_to_depth.process(depth_frame)
        depth_frame = depth_frame.as_depth_frame()

        color_frame = np.fliplr(np.asanyarray(color_frame.get_data()))
        depth_frame = np.fliplr(np.asanyarray(depth_frame.get_data()))

        return [color_frame, depth_frame]

    def reset(self):
        """Resets the camera"""
        import pyrealsense2 as rs
        ctx = rs.context()
        devices = ctx.query_devices()
        for dev in devices:
            dev.hardware_reset()
