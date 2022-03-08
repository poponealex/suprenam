import re
from pathlib import Path
from platform import platform as get_platform_long_string
from shutil import which

from src.user_errors import *

SUPPORTED_OS = ("Windows", "Linux", "macOS", "mockOS")  # mockOS is for testing only.


def get_editor_command(
    editable_file_path: Path,
    favorite_editor_filename: str = "FAVORITE_EDITOR",
    platform: str = "",
) -> str:
    """
    Retrieve a command launching a text editor on a given text file.
    Args:
        editable_file_path: the path to the text file to edit.
        favorite_editor_filename: the name of the file defining the favorite editor (for testing only).
        platform: the OS on which the text file will be edited (automatic, for testing only).
    Returns:
        A string representing the complete command to open this file in a text editor.
    Raises:
        UnsupportedOSError: if the OS is not in SUPPORTED_OS.
        NoEditorCommandsFileError: if `editor_commands.md` is not found.
        NoEditorError: if no command-line capable editor is installed.
    """
    # Check whether the user has defined a favorite editor and it is installed.
    favorite_editor_path = Path.home() / ".suprenam" / favorite_editor_filename
    if favorite_editor_path.is_file():
        command = favorite_editor_path.read_text().strip()
        name = str(command).partition(" ")[0]  # make mypy happy
        if platform == "mockOS" or which(name):  # https://stackoverflow.com/a/34177358/173003
            return f"{command} {editable_file_path}"
        else:
            raise UninstalledFavoriteEditor(
                f"The editor command `{name}` is not found. "
                "You can either install the corresponding application "
                f"or delete the file `~/.suprenam/{favorite_editor_filename}`."
            )

    # Otherwise, calculate the platform name (during tests, ).
    platform = platform or get_platform_long_string().partition("-")[0]
    if platform not in SUPPORTED_OS:
        raise UnsupportedOSError(f"Unsupported operating system: {platform}.")

    # Retrieve a list of known editor commands.
    for editor_commands_folder in (".", "src"):
        editor_commands_path = Path(editor_commands_folder) / "editor_commands.md"
        if editor_commands_path.is_file():
            text = editor_commands_path.read_text()
            break
    else:
        raise NoEditorCommandsFileError(f"The file 'editor_commands.md' is not found.")

    # Among the commands known to work on the platform, return the first one that is installed.
    supported_commands = re.compile(r"(?m)- \*\*.+\*\* \(.*?%s.*?\): `(.+?)`" % platform).findall
    for command in supported_commands(text):
        name = str(command).partition(" ")[0]  # make mypy happy
        if platform == "mockOS" or which(name):  # https://stackoverflow.com/a/34177358/173003
            return f"{command} {editable_file_path}"

    # If no known command is installed, raise an error.
    raise (NoEditorError(f"No text editor found for the platform {platform}."))
