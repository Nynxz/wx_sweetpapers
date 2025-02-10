#!/usr/bin/env python
import imageio.v3 as iio

import subprocess
import json
import argparse
import os
import random
import time
import signal
from utils.colors import bcolors, wx_log
from collections import defaultdict
from dataclasses import dataclass


@dataclass
class TransitionData:
    ttype: str
    tduration: str
    tstep: str
    tfill_mode: str
    tfps: str
    tmode: str


def get_transition_config(config):
    return TransitionData(
        config["defaults"].get("transition_type"),
        config["defaults"].get("transition_duration"),
        config["defaults"].get("transition_step"),
        config["defaults"].get("fill_mode"),
        config["defaults"].get("transition_fps"),
        config["defaults"].get("mode"),
    )


def construct_swww_cmd(tdata: TransitionData, monitor, img):
    command = f"swww img -o {monitor} '{img}' --resize {
        tdata.tfill_mode
    } --transition-type {tdata.ttype} --transition-duration {
        tdata.tduration
    } --transition-step {tdata.tstep} --transition-fps {tdata.tfps}"
    print(command)
    return command


def swap_monitor_background(tdata, config, screen, img):
    monitor = config["screens"].get(str(screen))
    command = construct_swww_cmd(tdata, monitor, img)
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        wx_log(f"Swapped Screen {monitor} to {img}", bcolors.OKGREEN)
        if result.stdout:
            print("Output: ", result.stdout)
        if result.stderr:
            print("Errors: : ", result.stderr)
    except subprocess.CalledProcessError as e:
        print(
            f"Command failed with errors: {e}\n {
                bcolors.WARNING
            } Is swww-daemon running? {bcolors.ENDC}"
        )


def change_wallpaper(config, profile, path=None):
    if path is not None:
        path = path
    else:
        path = os.path.expandvars(config["defaults"].get("packs_location"))
        path = os.path.join(path, profile)
        print(path)
    print("HELLO")
    print(path)
    tdata = get_transition_config(config)

    directories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    directories.sort()
    print(directories)
    wx_log("STARTING WX_SWEETPAPERS", bold=True, underline=True)
    wx_log(
        f"Found {len(directories)} Directories in {profile} \n- {'- '.join([f'{path}/{x}\n' for x in directories])}"
    )

    last_d = directories[0]
    last_d_i = 0

    # img_path = os.path.join(path, last_d)
    # imgs = [(f.split(".")[0], os.path.join(img_path, f)) for f in os.listdir(img_path)]
    # imgs = [(f.split(".")[0], os.path.join(img_path, f)) for f in os.listdir(img_path)]
    # wx_log(f"\nSwapping to {img_path}", bold=True, underline=True)
    # imgs = pick_random_image_from_alphapack(imgs, config)
    # print(imgs)
    # Quick Swap all monitors
    # for i in range(len(imgs)):
    #    print(imgs[i])
    #    screen, img = imgs[i]
    #    screen = config["screens"].get(screen)
    #    print(config["screens"].get("1"))
    #   print(screen)
    #   print(img)
    #   swap_monitor_background(tdata, config, screen, str(img))
    # time.sleep(config["defaults"].get("interval"))

    while True:
        if len(directories) > 1:
            if tdata.tmode == "ordered":
                last_d = directories[last_d_i]
                last_d_i += 1
                if last_d_i >= len(directories):
                    last_d_i = 0
            else:
                last_d = random.choice([d for d in directories if d != last_d])

        # split into tuple - 1.jpg 2.jpg (screen, image_path)
        img_path = os.path.join(path, last_d)
        imgs = [
            (f.split(".")[0], os.path.join(img_path, f)) for f in os.listdir(img_path)
        ]

        wx_log(f"\nSwapping to {img_path}", bold=True, underline=True)

        if not len(imgs):
            wx_log(f"No Images Found in: {os.path.join(path, last_d)}", bcolors.WARNING)
            continue
        imgs = pick_random_image_from_alphapack(imgs, config)
        # Swap Monitors
        print(imgs)
        for screen, img in imgs:
            print(screen, img)
            print(config["screens"].get(str(screen)))
            swap_monitor_background(tdata, config, screen, img)
            # Swap Monitors 1 at a time
            if config["defaults"].get("sequence") != "true":
                time.sleep(config["defaults"].get("interval"))
        if config["defaults"].get("sequence") == "true":
            time.sleep(config["defaults"].get("interval"))


def is_landscape(path):
    result = subprocess.run(
        ["exiftool", "-json", path], stdout=subprocess.PIPE, text=True
    )

    # Parse the JSON output
    metadata = json.loads(result.stdout)[0]

    # Extract resolution
    width = metadata.get("ImageWidth")
    height = metadata.get("ImageHeight")
    # height, width = iio.imread(path).shape[:2]
    return height < width


def pick_random_image_from_alphapack(imgs, config):
    print("Picking images")
    groups = defaultdict(list)

    for _, path in imgs:
        orientation = "Landscape" if is_landscape(path) else "Portrait"
        groups[orientation].append(path)
        # match = re.match(r"(\d+)", name)  # Extract numeric prefix
        # if match:
        # cleaned_name = re.sub(r"[a-zA-Z]", "", name)
        #     index = int(match.group(1))  # Convert to integer
        #    orientation = groups["Landscape" if is_landscape(path) else "Portrait"].append((str))
        #    groups[index].append((str(index), path))

    # print(groups)
    # wx_log(
    #    f"{'\n'.join([f'{key} {config["screens"].get(str(key))} : \n-{"".join(["\n-".join([y[1] for y in value])])}' for key, value in groups.items()])}"
    # )
    # wx_log("Possibilities", underline=True)

    # wx_log(
    #    f"{'\n'.join([f'{config["screens"].get(str(key))} : {len(value)}' for key, value in groups.items()])}"
    # )

    # wx_log(
    #   f"{'\n'.join([f'{config["screens"].get(str(key))} : {["Landscape" if is_landscape(z[1]) else "Portrait" for z in value]}' for key, value in groups.items()])}"
    # )

    landscape = 1
    portrait = 2

    selected_files = [
        (2, random.choice(groups["Portrait"])),
        (1, random.choice(groups["Landscape"])),
        (3, random.choice(groups["Portrait"])),
    ]
    # selected_files = [random.choice(group) for group in groups.values()]
    # custom order (R(2) > Middle(0) > L(1))

    print(selected_files)
    # Sort 1-3
    try:
        selected_files = sorted(selected_files, key=lambda x: x[0], reverse=True)
        # Swap Middle(1)[2] and Left(2)[1]
        (selected_files[2], selected_files[1]) = (selected_files[1], selected_files[2])
    except Exception as e:
        wx_log(f"Failed swap: {e}", bcolors.FAIL)
    # Reverse Order
    # selected_files = selected_files[::-1]
    print("Picked images")

    wx_log("SELECTED", underline=True)
    # wx_log(
    #   f"{'\n'.join([f'{"".join([":".join([y for y in value])])}' for value in selected_files])}"
    # )
    return selected_files


def debug_startup(config_data):
    if config_data["defaults"].get("debug"):
        debug = config_data["defaults"].get("debug")
        if debug:
            for section, config in config_data.items():
                if isinstance(config, dict):
                    print(f"\nSection: {section}")
                    for key, value in config.items():
                        print(f"{key} = {value}")
                elif isinstance(config, list):
                    print(f"\nSection: {section}")
                    for item in config:
                        print(item)


def is_process_running(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


def shutdown_already_running():
    print(f"PID: {os.getpid()}")
    pid_file = "/tmp/wx_sweetpapers.pid"
    try:
        with open(pid_file, "r") as f:
            last_pid = int(f.read().strip())
            print(f"Last PID: {last_pid}")
            if is_process_running(last_pid):
                print(
                    f"{bcolors.FAIL}Killing already running process {last_pid}{
                        bcolors.ENDC
                    }"
                )
                os.kill(last_pid, signal.SIGTERM)
    except (ProcessLookupError, FileNotFoundError, ValueError):
        print(f"Creating PID file @ {pid_file}")

    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))


def load_config():
    parser = argparse.ArgumentParser(description="wx_sweetpapers")
    parser.add_argument("-c", "--config", help="Path to the custom config file")
    parser.add_argument("-p", "--profile", help="Path to the wallpaper pack profile")
    parser.add_argument("-P", "--path", help="Path to the wallpaper pack profile")
    args = parser.parse_args()
    if not args.config:
        parser.error("Please provide the path to the config file using -c flag")
    if not args.profile:
        args.profile = None
    if not args.path:
        args.path = None

    with open(args.config, "r") as config_file:
        try:
            return (json.load(config_file), args.profile, args.path)
        except json.JSONDecodeError as e:
            print(f"Error parsing Config File: {e}")
            exit()


def main():
    shutdown_already_running()
    [config_data, profile, path] = load_config()
    debug_startup(config_data)
    change_wallpaper(config_data, profile, path)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting wx_sweetpapers")
