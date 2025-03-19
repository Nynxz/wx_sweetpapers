from collections import defaultdict
import json
import os
import random
import re
import subprocess

from utils.colors import bcolors, wx_log
from utils.config import TransitionData


def get_directories(path):
    directories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    directories.sort()

    return directories


def get_orientations(path):
    result = subprocess.run(
        ["extras/rst-orientation/target/release/rst-orientation", path],
        stdout=subprocess.PIPE,
        text=True,
    )
    return result.stdout.strip().split("\n")


def get_images_from_path(img_path):
    imgs = [(f.split(".")[0], os.path.join(img_path, f)) for f in os.listdir(img_path)]
    return imgs


def get_next_directory(
    transition_data: TransitionData, directories: list, current_index
):
    if len(directories) > 1:
        if transition_data.tnext == "ordered":
            next_directory = directories[current_index]
        else:
            next_directory = random.choice(
                [d for i, d in enumerate(directories) if i != current_index]
            )
        return next_directory
    return directories[current_index]


def get_pack_image_orientations(path, orientation_cache):
    if path not in orientation_cache:
        wx_log(f"Caching {path}", bcolors.WARNING)
        orientation_cache[path] = {"landscape": [], "portrait": []}
        orientations = get_orientations(path)
        hm = [x.split(",") for x in orientations]
        for img_path, b_landscape in hm:
            orientation_cache[path][b_landscape].append(img_path)
        imgs = orientation_cache[path]
    else:
        wx_log(f"Got From Cache: {path}")
        imgs = orientation_cache[path]
    return imgs


def pick_random_image_from_alphapack(imgs, config):
    groups = defaultdict(list)
    for name, path in imgs:
        match = re.match(r"(\d+)", name)  # Extract numeric prefix
        if match:
            index = int(match.group(1))  # Convert to integer
            groups[index].append((str(index), path))
    wx_log("Possibilities", underline=True)

    wx_log(
        f"{'\n'.join([f'{config["screens"].get(str(key))} : {len(value)}' for key, value in groups.items()])}"
    )
    selected_files = [random.choice(group) for group in groups.values()]
    # custom order (R(2) > Middle(0) > L(1))

    # Sort 1-3
    try:
        selected_files = sorted(selected_files, key=lambda x: x[0], reverse=True)
        # Swap Middle(1)[2] and Left(2)[1]
        (selected_files[2], selected_files[1]) = (selected_files[1], selected_files[2])
    except Exception as e:
        wx_log(f"Failed swap: {e}", bcolors.FAIL)
    #
    # Reverse Order
    # selected_files = selected_files[::-1]

    wx_log("SELECTED", underline=True)
    wx_log(
        f"{'\n'.join([f'{"".join([":".join([y for y in value])])}' for value in selected_files])}"
    )
    return selected_files


def pick_random_image_from_orientations(orientations, config, last_images=[]):
    to_swap = []
    for screen in config["screens"]:
        screen_orientation = config["screens"][screen]["orientation"]
        to_swap.append(
            (
                screen,
                random.choice(
                    [
                        img
                        for img in orientations[
                            "portrait"
                            if screen_orientation == "portrait"
                            and len(orientations["portrait"])
                            else "landscape"
                        ]
                        # If there is only 1 image use it
                        if len(orientations[screen_orientation]) <= 1
                        # Theres more than one possibility, dont swap to whats already active
                        or img not in last_images
                    ]
                ),
            )
        )
    return to_swap
