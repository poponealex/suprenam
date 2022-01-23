import re
import subprocess
from pathlib import Path
from platform import platform as get_platform_string

from src.goodies import print_fail
from src.user_errors import *


OS = {
    "macOS": {
        "QUERY_ALL_DEFAULTS_COMMAND": [
            "defaults",
            "read",
            "com.apple.LaunchServices/com.apple.launchservices.secure",
            "LSHandlers",
        ],
        "EXTRACT_EDITOR": r'(?ms)\s*\{\s*LSHandlerContentType = "public\.plain-text";\s*LSHandlerPreferredVersions =\s*\{\s*LSHandlerRoleAll = "-";\s*\};\s*LSHandlerRoleAll = "([\w.]+)";',
        "DEFAULT_EDITOR_COMMAND": {
            "com.microsoft.vscode": ["code", "-w"],
            "com.sublimetext.3": ["subl", "-w"],
        },  # TODO: add different versions of Sublime Text
        "FALLBACK_EDITOR_COMMAND": [
            "open",
            "-n",  # open a new instance of the application even if one is already running
            "-t",  # open with the default text editor
            "-W",  # block until the **application** is closed (even if it was already running).
            #        This is far from ideal, but there is currently no per-window way to check
        ],
    },
    "Linux": {
        "QUERY_ALL_DEFAULTS_COMMAND": [
            "xdg-mime",
            "query",
            "default",
            "text/plain",
        ],
        "EXTRACT_EDITOR": r"^(.*)\.desktop$",
        "DEFAULT_EDITOR_COMMAND": {
            "code": [
                "code",
                "-w", # wait for the file to be closed before returning
            ],
            "sublime_text": ["subl", "-w"],
        },
        "FALLBACK_EDITOR_COMMAND": ["open", "-w"],
    },
    # TODO: add Windows
}


def get_editor_command(path: Path) -> list:
    """
    Retrieve a command launching a text editor on a given text file.

    Args:
        path: the path to the text file to edit.

    Returns:
        A list of strings representing the command to launch the system's default text editor
        on the given text file. If no default text editor is defined, a suitable fallback command
        is returned.

    Raises:
        UnsupportedOSError: if the OS dictionary defines no key for the given operating system name.
    """
    platform_string = get_platform_string().split("-")[0]
    os_dict = OS.get(platform_string)
    if not os_dict:
        print_fail(
            f"Unsupported operating system: {platform_string}. "
            f"Supported operating systems are: {', '.join(OS.keys())}"
        )
        raise UnsupportedOSError(platform_string)

    try:
        output = subprocess.run(
            list(os_dict["QUERY_ALL_DEFAULTS_COMMAND"]),  # make mypy happy
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        ).stdout
    except subprocess.CalledProcessError as e:
        print_fail(str(e))  # make mypy happy
        raise e

    default_editor_handler = re.findall(str(os_dict["EXTRACT_EDITOR"]), output)  # make mypy happy
    if default_editor_handler and os_dict.get(default_editor_handler[0]) is not None:
        command = os_dict["DEFAULT_EDITOR_COMMAND"][default_editor_handler[0]]  # type: ignore
    else:
        command = list(os_dict["FALLBACK_EDITOR_COMMAND"])  # make mypy happy
    return command + [str(path)]
