import re
import subprocess
from pathlib import Path

from src.goodies import print_warning


OS = {
    "macOS": {
        "QUERY_DEFAULTS_COMMAND": [
            "defaults",
            "read",
            "com.apple.LaunchServices/com.apple.launchservices.secure",
            "LSHandlers",
        ],
        "REGEX": r'(?ms)\s*\{\s*LSHandlerContentType = "public\.plain-text";\s*LSHandlerPreferredVersions =\s*\{\s*LSHandlerRoleAll = "-";\s*\};\s*LSHandlerRoleAll = "([\w.]+)";',
        "DEFAULT_COMMAND": [
            "/usr/bin/open",
            "-neW",
        ],
        "EDITOR_COMMAND": {
            "com.microsoft.vscode": ["/usr/local/bin/code", "-w"],
            "com.sublimetext.3": ["/usr/local/bin/subl", "-w"],
        },  # TODO: add different versions of Sublime Text
    },
    "Linux": {
        "QUERY_DEFAULTS_COMMAND": [
            "xdg-mime",
            "query",
            "default",
            "text/plain",
        ],
        "REGEX": r"^(.*)\.desktop$",
        "DEFAULT_COMMAND": ["/bin/open", "-w"],
        "EDITOR_COMMAND": {
            "code": ["/usr/bin/code", "-w"],
            "sublime_text": ["/usr/bin/subl", "-w"],
        },
    },
}


def get_editor_command(os_name: str = "") -> str:
    """
    Retrieve the system's default text editor.

    Args:
        os_name: operating system's name
            macOS and Linux (with XDG utils installed) currently supported

    Returns:
        The default text editor's command name for supported editors.
        The `open -w` command for an unsupported or undefined editor.

    Raises:
        UnsupportedOS Error if the os is not supported.
    """
    os = OS.get(os_name)
    if not os:
        raise UnsupportedOS("OS not yet supported.")
    parse_output = re.compile(os["REGEX"]).findall
    try:
        result = parse_output(
            subprocess.run(
                os["QUERY_DEFAULTS_COMMAND"],
                encoding="utf-8",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            ).stdout
        )
        if result:
            if not Path(os["EDITOR_COMMAND"][result[0]][0]).exists():
                raise BinaryNotFound(f"Please add a symbolic link for {result[0]} to {os['EDITOR_COMMAND'][result[0]][0]}")
            return os["EDITOR_COMMAND"][result[0]]
    except (subprocess.CalledProcessError, KeyError) as e:
        print_warning(e)
    return os["DEFAULT_COMMAND"]


class UnsupportedOS(Exception):
    ...


class BinaryNotFound(Exception):
    ...
