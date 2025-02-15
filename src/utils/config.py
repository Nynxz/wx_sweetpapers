import argparse
import json
from dataclasses import dataclass
import os


@dataclass()
class TransitionData:
    tnext: str
    tfill_mode: str
    tinterval: int
    ttype: str
    tduration: str
    tstep: str
    tfps: str


def get_pack_location(config, profile):
    pack_location = os.path.expanduser(config["defaults"].get("packs_location"))
    if profile is not None:
        pack_location = os.path.join(pack_location, profile)
    return pack_location


def get_transition_config(config):
    return TransitionData(
        config["transition"].get("next"),
        config["transition"].get("fill_mode"),
        config["transition"].get("interval"),
        config["transition"].get("transition_type"),
        config["transition"].get("transition_duration"),
        config["transition"].get("transition_step"),
        config["transition"].get("transition_fps"),
    )


def load_config():
    parser = argparse.ArgumentParser(description="wx_sweetpapers")
    parser.add_argument("-c", "--config", help="Path to the custom config file")
    parser.add_argument("-p", "--profile", help="Path to the wallpaper pack profile")
    args = parser.parse_args()
    if not args.config:
        parser.error("Please provide the path to the config file using -c flag")
    if not args.profile:
        parser.error("Please provide a profile with -p")

    with open(args.config, "r") as config_file:
        try:
            return (json.load(config_file), args.profile)
        except json.JSONDecodeError as e:
            print(f"Error parsing Config File: {e}")
            exit()
