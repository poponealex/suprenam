import re
import subprocess
from pathlib import Path
from platform import platform as get_platform_long_string
from shutil import which
from typing import Optional

from src.user_errors import *

OS = {
    "macOS": {
        "QUERY_ALL_DEFAULTS_COMMAND": "defaults read com.apple.LaunchServices/com.apple.launchservices.secure LSHandlers",
        "EXTRACT_EDITOR": r'(?ms)\s*\{\s*LSHandlerContentType = "public\.tab-separated-values-text";\s*LSHandlerPreferredVersions =\s*\{\s*LSHandlerRoleAll = "-";\s*\};\s*LSHandlerRoleAll = "([\w.]+)";',
        "CUSTOM_EDITOR_COMMAND": {
            "com.microsoft.vscode": ["code", "-w"],
            "com.sublimetext.3": ["subl", "-w"],  # TODO: add different versions of Sublime Text
            "com.macromates.textmate": ["mate", "-w"],
        },
        "FALLBACK_EDITOR_COMMAND": [
            "open",
            "-n",  # open a new instance of the application even if one is already running
            "-e",  # open with TextEdit
            "-W",  # block until the **application** is closed (even if it was already running).
            #        This is far from ideal, but there is currently no per-window way to check
        ],
    },
    "Linux": {
        "QUERY_ALL_DEFAULTS_COMMAND": "xdg-mime query default text/tab-separated-values",
        "EXTRACT_EDITOR": r"^(.*)\.desktop$",
        "CUSTOM_EDITOR_COMMAND": {
            "code": ["code", "-w"],
            "sublime_text": ["subl", "-w"],
        },
        "FALLBACK_EDITOR_COMMAND": ["open", "-w"],
    },
    # TODO: add Windows
}


def is_tool(name):  # https://stackoverflow.com/a/34177358/173003
    """Check whether `name` is on PATH and marked as executable."""
    return which(name) is not None


def get_editor_command(path: Path, platform: Optional[str] = None) -> list:
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
    platform = platform or get_platform_long_string().partition("-")[0]
    os_dict = OS.get(platform)
    if not os_dict:
        raise UnsupportedOSError(
            f"Unsupported operating system: {platform}. "
            f"Supported operating systems are: {', '.join(OS.keys())}."
        )

    try:
        output = subprocess.run(
            str(os_dict["QUERY_ALL_DEFAULTS_COMMAND"]).split(),  # make mypy happy
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        ).stdout
    except Exception as e:
        raise RetrieveDefaultsError(f"Failed to retrieve the defaults: {e}.")

    match = re.search(str(os_dict["EXTRACT_EDITOR"]), output)  # make mypy happy
    custom_editor_handler = match.group(1) if match else ""

    # Check whether the user has defined a custom editor
    command = os_dict["CUSTOM_EDITOR_COMMAND"].get(custom_editor_handler)  # type: ignore
    if command and is_tool(command[0]):  # is the command both known and installed on the system?
        return command + [str(path)]

    # Otherwise, try to find another editor which is both known and installed on the system
    for command in os_dict["CUSTOM_EDITOR_COMMAND"].values():  # type: ignore
        if is_tool(command[0]):
            return command + [str(path)]

    # Otherwise, return the fallback command defined by the system
    # (on macOS, this is TextEdit, which lacks an option to wait for the file to be closed)
    return list(os_dict["FALLBACK_EDITOR_COMMAND"]) + [str(path)]  # make mypy happy
