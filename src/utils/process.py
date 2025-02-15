import os
import signal

from utils.colors import bcolors


def is_process_running(pid):
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


def create_wx_pid(pid_file):
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))


def shutdown_already_running():
    """
    Checks if there is an already running wx_sweetpapers process
    Trying to kill it, then creating a new pid_file
    """
    # Current PID
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
    create_wx_pid(pid_file)
