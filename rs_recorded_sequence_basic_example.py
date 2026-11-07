## License: Apache 2.0. See LICENSE file in root directory.
## Copyright(c) 2015-2017 RealSense, Inc. All Rights Reserved.

"""Display recorded RealSense RGB and depth frames without alignment."""

import argparse
from pathlib import Path

import pyrealsense2 as rs
import numpy as np
import cv2


def main():
    parser = argparse.ArgumentParser(
        description="Display RGB and depth from a RealSense .bag recording."
    )
    parser.add_argument("path", nargs="?", help="Path to the RealSense .bag file")
    args = parser.parse_args()
    recording_path = args.path or input("Insert path to the RealSense .bag file as first argument or here:")
    recording_path = Path(recording_path.strip().strip('"')).expanduser()
    if not recording_path.is_file():
        parser.error("Recording file not found: {}".format(recording_path))
    if recording_path.suffix.lower() != ".bag":
        parser.error("Use a RealSense .bag recording containing RGB and depth.")

    pipeline = rs.pipeline()
    config = rs.config()
    config.enable_device_from_file(str(recording_path.resolve()), repeat_playback=False)
    # Use recorded resolutions and frame rates rather than forcing live settings.
    config.enable_stream(rs.stream.depth)
    config.enable_stream(rs.stream.color)

    profile = pipeline.start(config)
    try:
        playback = profile.get_device().as_playback()
        playback.set_real_time(True)

        depth_colorizer = rs.colorizer()
        depth_colorizer.set_option(rs.option.color_scheme, 0)
        depth_colorizer.set_option(rs.option.histogram_equalization_enabled, 1)
        window_name = "RealSense - Recorded sequence"
        cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)

        while True:
            success, frames = pipeline.try_wait_for_frames(1000)
            if not success:
                if playback.current_status() == rs.playback_status.stopped:
                    print("End of recording.")
                    break
                key = cv2.waitKey(1) & 0xFF
                if key in (27, ord("q")) or cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break
                continue

            depth_frame = frames.get_depth_frame()
            color_frame = frames.get_color_frame()
            if not depth_frame or not color_frame:
                continue

            # Recordings can store color in a different format than live BGR8.
            color_image = np.asanyarray(color_frame.get_data())
            color_format = color_frame.get_profile().format()
            conversions = {
                rs.format.rgb8: cv2.COLOR_RGB2BGR,
                rs.format.rgba8: cv2.COLOR_RGBA2BGR,
                rs.format.bgra8: cv2.COLOR_BGRA2BGR,
                rs.format.yuyv: cv2.COLOR_YUV2BGR_YUY2,
            }
            if color_format in conversions:
                color_image = cv2.cvtColor(color_image, conversions[color_format])
            elif color_format != rs.format.bgr8:
                raise RuntimeError("Unsupported recorded color format: {}".format(color_format))

            colorized_depth_frame = depth_colorizer.colorize(depth_frame)
            depth_colormap = cv2.cvtColor(
                np.asanyarray(colorized_depth_frame.get_data()), cv2.COLOR_RGB2BGR
            )

            # Resize for side-by-side display only; no geometric alignment.
            if color_image.shape != depth_colormap.shape:
                color_image = cv2.resize(
                    color_image,
                    (depth_colormap.shape[1], depth_colormap.shape[0]),
                    interpolation=cv2.INTER_AREA,
                )
            images = np.hstack((color_image, depth_colormap))
            cv2.imshow(window_name, images)
            key = cv2.waitKey(1) & 0xFF
            if key in (27, ord("q")) or cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                break
    finally:
        pipeline.stop()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
