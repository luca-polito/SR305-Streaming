## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 RealSense, Inc. All Rights Reserved.

###############################################
##      Open CV and Numpy integration        ##
###############################################

import pyrealsense2 as rs
import numpy as np
import cv2

# Configure depth and color streams
pipeline = rs.pipeline()
config = rs.config()

# Get device product line for setting a supporting resolution
pipeline_wrapper = rs.pipeline_wrapper(pipeline)
pipeline_profile = config.resolve(pipeline_wrapper)
device = pipeline_profile.get_device()
device_product_line = str(device.get_info(rs.camera_info.product_line))

found_rgb = False
for s in device.sensors:
    if s.get_info(rs.camera_info.name) == 'RGB Camera':
        found_rgb = True
        break
if not found_rgb:
    print("The demo requires Depth camera with Color sensor")
    exit(0)

config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

# Start streaming
profile = pipeline.start(config)

try:
    # Use the native RealSense Jet palette with automatic depth contrast.
    depth_colorizer = rs.colorizer()
    depth_colorizer.set_option(rs.option.color_scheme, 0)
    depth_colorizer.set_option(rs.option.histogram_equalization_enabled, 1)

    # Enable automatic exposure on the RGB sensor to adapt to scene lighting.
    color_sensor = profile.get_device().first_color_sensor()
    if color_sensor.supports(rs.option.enable_auto_exposure):
        try:
            color_sensor.set_option(rs.option.enable_auto_exposure, 1)
            print("RGB auto exposure enabled. Allow a few seconds to adjust.")
        except RuntimeError as error:
            print("Could not enable RGB auto exposure:", error)
    else:
        print("RGB auto exposure is not supported by this sensor.")

    while True:

        # Wait for a coherent pair of frames: depth and color
        frames = pipeline.wait_for_frames()
        depth_frame = frames.get_depth_frame()
        color_frame = frames.get_color_frame()
        if not depth_frame or not color_frame:
            continue

        # Convert images to numpy arrays
        depth_image = np.asanyarray(depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # RealSense produces RGB8; OpenCV displays images in BGR order.
        colorized_depth_frame = depth_colorizer.colorize(depth_frame)
        depth_colormap = cv2.cvtColor(
            np.asanyarray(colorized_depth_frame.get_data()), cv2.COLOR_RGB2BGR
        )

        depth_colormap_dim = depth_colormap.shape
        color_colormap_dim = color_image.shape

        # If depth and color resolutions are different, resize color image to match depth image for display
        if depth_colormap_dim != color_colormap_dim:
            resized_color_image = cv2.resize(color_image, dsize=(depth_colormap_dim[1], depth_colormap_dim[0]), interpolation=cv2.INTER_AREA)
            images = np.hstack((resized_color_image, depth_colormap))
        else:
            images = np.hstack((color_image, depth_colormap))

        # Show images
        cv2.namedWindow('RealSense', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('RealSense', images)
        cv2.waitKey(1)

finally:

    # Stop streaming
    pipeline.stop()
