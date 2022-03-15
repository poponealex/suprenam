import re
from pathlib import Path
from shutil import which

from src.user_errors import *
from src.context import Context


def get_editor_command(
    context: Context,
    editable_file_path: Path,
) -> str:
    """
    Retrieve a command launching a text editor on a given text file.
    Args:
        context: all data relative to the current execution context (platform, logger, etc.).
        editable_file_path: the path to the text file to edit.
    Returns:
        A string representing the complete command to open this file in a text editor.
    Raises:
        NoEditorCommandsFileError: if `editor_commands.md` is not found.
        NoEditorError: if no command-line capable editor is installed.
        UninstalledFavoriteEditorError: if the favorite editor is not installed.
    """
    # Check whether the user has defined a favorite editor and it is installed.
    command = context.config.get("editor_command")
    if command:
        name = str(command).partition(" ")[0]  # make mypy happy
        if context.platform == "mockOS" or which(name):  # https://stackoverflow.com/a/34177358/173003
            return f"{command} {editable_file_path}"
        else:
            raise UninstalledFavoriteEditorError(
                f"The command '{name}' is not found. "
                "You can either install the corresponding editor "
                f"or modify it in '{context.workspace / 'config.json'}'."
            )

    # Retrieve a list of known editor commands.
    for editor_commands_folder in (".", "src"):
        editor_commands_path = Path(editor_commands_folder) / "editor_commands.md"
        if editor_commands_path.is_file():
            text = editor_commands_path.read_text()
            break
    else:
        raise NoEditorCommandsFileError(f"The file 'editor_commands.md' is not found.")

    # Among the commands known to work on the current platform, return the first one that is installed.
    supported_commands = r"(?m)^\|.+?\|.*?%s.*?\| *`(.+?)` *\|" % context.platform
    for command in re.findall(supported_commands, text):
        name = str(command).partition(" ")[0]  # make mypy happy
        if context.platform == "mockOS" or which(name):  # https://stackoverflow.com/a/34177358/173003
            return f"{command} {editable_file_path}"

    # If no known command is installed, raise an error.
    raise NoEditorError(f"No text editor found for the platform {context.platform}.")
