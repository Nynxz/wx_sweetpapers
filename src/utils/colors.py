from enum import Enum


class bcolors(Enum):
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def wx_log(tolog="", color: bcolors = bcolors.OKGREEN, bold=False, underline=False):
    print(
        f"{bcolors.UNDERLINE.value if underline else ''}{bcolors.BOLD.value if bold else ''}{color.value}{tolog}{bcolors.ENDC.value}"
    )
