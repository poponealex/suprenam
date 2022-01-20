from pathvalidate import validate_filename
from typing import List

from src.user_types import Clause, Name, Inode, InodePaths, EditedText


def parse_edited_text(
    text: EditedText,
    inode_paths: InodePaths,
    platform: str = "auto",  # enable testing on different platforms
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


class UnknownInodeError(ValueError):
    ...


class TabError(ValueError):
    ...
