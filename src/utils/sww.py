import subprocess
from utils.colors import bcolors, wx_log
from utils.config import TransitionData


def construct_swww_cmd(tdata: TransitionData, monitor, img):
    command = f"swww img -o {monitor} '{img}' --resize {
        tdata.tfill_mode
    } --transition-type {tdata.ttype} --transition-duration {
        tdata.tduration
    } --transition-step {tdata.tstep} --transition-fps {tdata.tfps}"
    print(command)
    return command


def swap_monitor_background(tdata, config, screen, img):
    monitor = config["screens"].get(screen)["name"]
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
