import subprocess
from pathlib import Path
from pathvalidate import validate_filename
from platform import platform as get_platform_string
from itertools import groupby
from tempfile import NamedTemporaryFile
from typing import List
from natsort import os_sorted  # type: ignore

from src.default_editor import get_editor_command
from src.user_types import Clause, Name, Inode, InodePaths, EditableText, EditedText


def get_editable_text(inode_paths: InodePaths) -> EditableText:
    """
    Being given a mapping of inodes (ints) to paths (Path objects), return a textual representation
    of these associations, sorted in natural order and grouped by common parent if needed.

    Args:
        inode_paths: dict of { inode: path }

    Returns:
        A string in either of these formats (tab-separated):
            1. If all files are siblings:
                inode   filename
                inode   filename
                ...
            2. Otherwise:
                common_ancestor/path/to/common_parent
                inode   filename
                inode   filename
                ...

                common_ancestor/path/to/common_parent
                inode   filename
                inode   filename
                ...

                ...

    """
    # Create a naturally sorted list of triples (parent, name, inode) with null paths filtered out
    parents_names_inodes = os_sorted(  # natural sort by parent, then name, then (useless) inode
        (
            f"\n{path.parent}",  # the prefix '\n' adds an empty line for maximal consistency
            path.name,
            inode,
        )
        for (inode, path) in inode_paths.items()
        if path.name  # null paths (empty or root) would make os_sorted raise a ValueError
    )

    # Group them by common parents
    groups = [
        (
            parent,
            list(children),  # converting the inner generator allows to use it twice (len + loop)
        )
        for (parent, children) in groupby(
            parents_names_inodes,
            key=lambda parent_name_inode: parent_name_inode[0],  # group by parent
        )
    ]

    # Format the result
    if len(groups) == 0:  # empty selection
        result = []
    elif len(groups) == 1:  # all files are siblings: showing their parent is useless
        result = [f"{inode}\t{name}" for (_, name, inode) in groups[0][1]]
    else:  # several groups of siblings: showing their parents may be useful for desambiguation
        result = []
        for (parent, children) in groups:
            result.append(f"{parent}")
            result.extend(f"{inode}\t{name}" for (_, name, inode) in children)
    return EditableText("\n".join(result))


def get_editable_file_path(inode_paths: InodePaths) -> Path:
    """
    Create a temporary file populated with the names of the files to rename.

    Args:
        inode_paths: dict of { inode : path }

    Returns:
        The temporary file's Path.
    """
    path = Path(NamedTemporaryFile(mode="w+", delete=False, suffix=".txt").name)
    path.write_text(get_editable_text(inode_paths))
    return path


def run_editor(editable_file_path: Path) -> EditedText:
    """
    Open the editable text on the system's default text editor to allow the user to perform the renamings.

    Args:
        editable_file_path: Path to the temporary file populated with the editable text.

    Returns:
        The text contained in editable_file_path when the user closes the editor's window.
    """
    platform = get_platform_string().split("-")[0]
    editor_command = get_editor_command(platform)
    subprocess.run(editor_command + [str(editable_file_path)], check=True)
    return EditedText(editable_file_path.read_text())


def parse_edited_text(
    text: EditedText,
    inode_paths: InodePaths,
    platform: str,
) -> List[Clause]:
    """
    Parse the renamings' text.

    Args:
        text: the text with the effective renamings.
        inode_paths: dict containing each path (value) with its inode (key).
        platform: OS on which the renamings will be performed.

    Raises:
        UnknownInodeError: the edited text contains an inode absent from the source text.
        TabError: a new name contains a tabulation. Although such a character is valid on most
            platforms, in the edited text it probably results from a typo.
        pathvalidate.ValidationError: a new name includes invalid character(s) for a filename
            (depends on the target platform).

    Returns:
        A list of Clause (path, new_name).
    """
    result = []
    for line in text.split("\n"):
        head, *tail = line.split("\t", maxsplit=1)
        if not tail:
            continue
        if not head.isdigit():
            continue
        inode = Inode(int(head))
        path = inode_paths.get(inode)
        if path is None:
            raise UnknownInodeError(f"Unknown inode {inode}.")
        new_name = tail[0]
        if "\t" in new_name:
            raise TabError(f"Illegal tabulation in the new name: {repr(new_name)}.")
        if path.name == new_name:
            continue
        validate_filename(new_name, platform=platform)
        result.append(Clause(path, Name(new_name)))
    return result


def edit_paths(
    paths: List[Path],
    get_inode=lambda path: path.stat().st_ino,  # enable testing with a fake (pure) inode getter
    get_edition_handler=get_editable_file_path,  # enable testing with a pure function returning a text
    edit=run_editor,  # enable simulating the user's editions
    platform: str = "auto",  # enable testing on different platforms
) -> List[Clause]:
    """
    Handle the user interface to edit paths, can be parameterized to work with a pure FileSystem.

    Args:
        paths: list of Paths to rename.
        get_inode: function called to get the inode.
        get_edition_handler: function called to get the text to write to the temporary file.
        edit: function called to run the editor.
        platform: OS on which the renamings will be performed.

    Returns:
        A list of Clause (path, new_name) with the effective renamings.
    """
    inode_paths = {Inode(get_inode(path)): path for path in paths}
    handler = get_edition_handler(inode_paths)
    text = edit(handler)
    clauses = parse_edited_text(text, inode_paths, platform=platform)
    return clauses


class UnknownInodeError(ValueError):
    ...


class TabError(ValueError):
    ...
