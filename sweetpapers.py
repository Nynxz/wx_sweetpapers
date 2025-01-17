#!/usr/bin/env python
import subprocess
import json
import argparse
import os
import random
import time
import signal


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def change_wallpaper(config, profile):
    path = os.path.expandvars(config["defaults"].get("packs_location"))
    if profile is not None:
        path = os.path.join(path, profile)

    # Transitions
    t_type = config["defaults"].get("transition_type")
    t_duration = config["defaults"].get("transition_duration")
    t_step = config["defaults"].get("transition_step")
    t_fps = config["defaults"].get("transition_fps")
    fill_mode = config["defaults"].get("fill_mode")

    directories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    print(directories)

    last_d = ""
    while True:
        if len(directories) > 1:
            last_d = random.choice([d for d in directories if d != last_d])
        else:
            last_d = directories[0]
        imgs = [
            (f.split(".")[0], os.path.join(path, last_d, f))
            for f in os.listdir(os.path.join(path, last_d))
        ]
        for screen, img in imgs:
            monitor = config["screens"].get(screen)
            command = f"swww img -o {monitor} {img} --resize {
                fill_mode
            } --transition-type {t_type} --transition-duration {
                t_duration
            } --transition-step {t_step} --transition-fps {t_fps}"
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                print(
                    f"{bcolors.OKGREEN}Swapped Screen {monitor} to {img} {bcolors.ENDC}"
                )
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
        time.sleep(config["defaults"].get("interval"))


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
    args = parser.parse_args()
    if not args.config:
        parser.error("Please provide the path to the config file using -c flag")
    if not args.profile:
        args.profile = None

    with open(args.config, "r") as config_file:
        try:
            return (json.load(config_file), args.profile)
        except json.JSONDecodeError as e:
            print(f"Error parsing Config File: {e}")
            exit()


def main():
    shutdown_already_running()
    [config_data, profile] = load_config()
    debug_startup(config_data)
    change_wallpaper(config_data, profile)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting wx_sweetpapers")
