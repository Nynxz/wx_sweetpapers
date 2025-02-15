#!/usr/bin/env python
import os
import random
import time
from utils.colors import wx_log

from utils.config import (
    get_pack_location,
    get_transition_config,
    load_config,
)
from utils.debug import debug_startup
from utils.image import (
    get_directories,
    get_images_from_path,
    get_next_directory,
    get_pack_image_orientations,
    pick_random_image_from_alphapack,
    pick_random_image_from_orientations,
)
from utils.process import shutdown_already_running
from utils.sww import swap_monitor_background


def start_wx_loop(config_data, profile):
    transition_data = get_transition_config(config_data)
    pack_location = get_pack_location(config_data, profile)
    directories = get_directories(pack_location)

    orientation_cache = {}
    last_images = []
    wx_log("STARTING WX_SWEETPAPERS", bold=True, underline=True)
    wx_log(
        f"Found {len(directories)} Directories in {profile} \n- {'- '.join([f'{pack_location}/{x}\n' for x in directories])}"
    )

    directory_index = 0
    while True:
        # Get Next Directory
        next_directory = get_next_directory(
            transition_data, directories, directory_index
        )
        next_directory_path = os.path.join(pack_location, next_directory)
        wx_log(str(next_directory_path))

        # If auto Orientation , cache pack orientations
        if config_data["defaults"].get("auto"):
            orientations = get_pack_image_orientations(
                next_directory_path, orientation_cache
            )
            to_swap = pick_random_image_from_orientations(
                orientations, config_data, last_images
            )
        else:
            # Regular Swap
            imgs = get_images_from_path(next_directory_path)
            to_swap = pick_random_image_from_alphapack(imgs, config_data)

        for screen, img in to_swap:
            swap_monitor_background(transition_data, config_data, screen, img)
            if config_data["defaults"].get("sequence"):
                time.sleep(transition_data.tinterval)

        # Increment
        directory_index += 1
        if directory_index >= len(directories):
            directory_index = 0
        # last_images = to_swap
        last_images = [x[1] for x in to_swap]
        wx_log(str(last_images))
        if not config_data["defaults"].get("sequence"):
            time.sleep(transition_data.tinterval)


def main():
    shutdown_already_running()
    [config_data, profile] = load_config()
    debug_startup(config_data)
    start_wx_loop(config_data, profile)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting wx_sweetpapers")
