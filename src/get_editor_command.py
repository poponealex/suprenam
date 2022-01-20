import re
import subprocess
from platform import platform as get_platform_string

from src.goodies import print_warning


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
            "-e",  # open with TextEdit
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


def get_editor_command() -> list:
    """
    Retrieve a command launching a text editor.

    Args:
        os_name: operating system's name.
            Currently supported (see global OS dictionary):
            - macOS
            - Linux (with XDG utils installed)

    Returns:
        A list of strings representing the command to launch the system's default text editor.
        If no default text editor is defined, a suitable fallback command is returned.

    Raises:
        UnsupportedOSError: if the OS dictionary defines no key for the given operating system name.
    """
    platform_string = get_platform_string().split("-")[0]
    os_dict = OS.get(platform_string)
    if not os_dict:
        raise UnsupportedOSError(
            f"Unsupported operating system: {platform_string}. "
            f"Supported operating systems are: {', '.join(OS.keys())}"
        )

    try:
        output = subprocess.run(
            list(os_dict["QUERY_ALL_DEFAULTS_COMMAND"]),  # make mypy happy
            encoding="utf-8",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        ).stdout
    except subprocess.CalledProcessError as e:
        print_warning(str(e))  # make mypy happy
        output = ""  # make the following regular expression fail

    default_editor_handler = re.findall(str(os_dict["EXTRACT_EDITOR"]), output)  # make mypy happy
    if default_editor_handler:
        return os_dict["DEFAULT_EDITOR_COMMAND"][default_editor_handler[0]]  # type: ignore
    else:
        return list(os_dict["FALLBACK_EDITOR_COMMAND"])  # make mypy happy


class UnsupportedOSError(Exception):
    ...
