import subprocess
import json
import argparse
import os
import random
import time


def change_wallpaper(config):
    path = os.path.expandvars(config["defaults"].get("packs_location"))
    directories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    print(directories)
    while True:
        d = random.choice(directories)
        # for d in directories:
        print(d)
        imgs = [
            (f.split(".")[0], os.path.join(path, d, f))
            for f in os.listdir(os.path.join(path, d))
        ]
        for i in imgs:
            monitor = config["screens"].get(i[0])
            print(monitor)
            print(i[1])
            command = f"swww img -o {monitor} {i[1]} --transition-type center"
            try:
                result = subprocess.run(
                    command,
                    shell=True,
                    check=True,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )

                print("Output: ", result.stdout)
                print("Errors: : ", result.stderr)
            except subprocess.CalledProcessError as e:
                print(f"Command failed with errors: {e}")
        time.sleep(10)


def debug_startup(config_data):
    for section, config in config_data.items():
        if isinstance(config, dict):
            print(f"\nSection: {section}")
            for key, value in config.items():
                print(f"{key} = {value}")
        elif isinstance(config, list):
            print(f"\nSection: {section}")
            for item in config:
                print(item)


def main():
    # Parse Arguments
    parser = argparse.ArgumentParser(description="wx_sweetpapers")
    parser.add_argument("-c", "--config", help="Path to the custom config file")

    args = parser.parse_args()
    if not args.config:
        parser.error("Please provide the path to the config file using -c flag")

    with open(args.config, "r") as config_file:
        try:
            config_data = json.load(config_file)
        except json.JSONDecodeError as e:
            print(f"Error parsing Config File: {e}")
            exit()

    if config_data["defaults"].get("debug"):
        debug = config_data["defaults"].get("debug")
        if debug:
            debug_startup(config_data)

    change_wallpaper(config_data)


if __name__ == "__main__":
    main()
