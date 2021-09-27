import subprocess
from pathlib import Path
from pathvalidate import validate_filename
from platform import platform
from itertools import groupby
from tempfile import NamedTemporaryFile
from typing import List

from src.default_editor import get_editor_command_name
from src.user_types import Clause


def get_editable_text(inode_paths: dict) -> str:
    """
    Get the text to output to the user's interface.

    Args:
        inode_paths: dict of { inode : path }

    Returns:
        A string in the either formats:
            1. If all files are siblings:
                inode   file name
                ...
            2. Else:
                /parent
                inode   file name
                ...
    """
    if not inode_paths:
        return ""
    result = []
    paths_and_inodes = sorted(
        ((path, inode) for (inode, path) in inode_paths.items()),
        key=lambda x: (x[0].parent, x[0].name),  # sorted by parent, then by name
    )
    # TODO for the name, use natural sort instead of lexicographic sort, and test thorougly
    groups = [
        (parent, list(children))  # converting to list prevents len(groups) to consume the generator
        for (parent, children) in groupby(paths_and_inodes, key=lambda item: item[0].parent)
    ]
    if len(groups) > 1:
        for (parent, children) in groups:
            result.append(f"\n{parent}\n")  # empty line before each parent for maximal consistency
            for (path, inode) in children:
                result.append(f"{inode}\t{path.name}\n")
    else:  # when all files to rename are siblings, it is useless to print their parent's path
        for (path, inode) in groups[0][1]:
            result.append(f"{inode}\t{path.name}\n")
    return "".join(result)


def get_editable_file_path(inode_paths: dict) -> Path:
    """
    Create a temporary file populated with the names of the files to rename.

    Args:
        inode_paths: dict of { inode : path }

    Returns:
        The temporary file's Path.
    """
    path = Path(NamedTemporaryFile(mode="w+", delete=False, suffix=".txt"))
    path.write_text(get_editable_text(inode_paths))
    return path


def run_editor(editable_file_path: Path) -> str:
    """
    Open the editable text on the system's default text editor to allow the user to perform the renamings.

    Args:
        editable_file_path: Path to the temporary file populated with the editable text.

    Returns:
        The text contained in editable_file_path when the user closes the editor's window.
    """
    editor = get_editor_command_name(platform().split("-")[0]) + [str(editable_file_path)]
    subprocess.run(editor, check=True)
    return editable_file_path.read_text()


def parse_edited_text(text: str, inode_paths, platform: str = platform().split("-")[0]) -> List[Clause]:
    """
    Parse the renamings' text.

    Args:
        text: the text with the effective renamings.
        inode_paths: dict containing each path (value) with its inode (key).
        find_all: regular expression to find all lines containing a renaming.

    Returns:
        A list of Clause (path, new_name).
    """
    result = []
    for line in text.split("\n"):
        inode, *tail = line.split("\t", maxsplit=1)
        if not inode.isdigit():
            continue
        path = inode_paths.get(int(inode))
        if not path:
            raise InodeError(f"This inode is invalid: '{inode}'.")
        new_name = tail[0]
        if "\t" in new_name:
            raise TabError(f"Illegal \\t character in the new name: '{new_name}'.")
        if Path(path).name != new_name:
            validate_filename(new_name, platform=platform)
            result += [Clause(path, new_name)]
    return result


def edit_paths(
    paths: List[Path],
    get_inode=lambda path: path.stat().st_ino,  # enable testing with a fake (pure) inode getter
    get_edition_handler=get_editable_file_path,  # enable testing with a pure function returning a text
    edit=run_editor,  # enable simulating the user's editions
):
    """
    Handle the user interface to edit paths, can be parameterized to work with a pure FileSystem.

    Args:
        paths: list of Paths to rename.
        get_inode: function to get the inode.
        get_edition_handler: function called to get the text to write to the temporary file.
        edit: function called to run the editor.

    Returns:
        A list of Clause (path, new_name) with the effective renamings.
    """
    inode_paths = {get_inode(path): path for path in paths}
    handler = get_edition_handler(inode_paths)
    text = edit(handler)
    clauses = parse_edited_text(text, inode_paths)
    return clauses


class InodeError(ValueError):
    ...


class TabError(ValueError):
    ...
