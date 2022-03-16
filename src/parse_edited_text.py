from typing import List, Optional

import pathvalidate

from src.user_errors import *
from src.user_types import Clause, EditedText, Inode, InodesPaths, Name


def parse_edited_text(
    text: EditedText,
    inodes_paths: InodesPaths,
    platform: Optional[str] = None,
) -> List[Clause]:
    """
    Parse the text in which the user has modified some filenames to specify a renaming.

    Args:
        text: the text with the desired renamings.
        inodes_paths: dict associating each inode to its path.
        platform: OS on which the renamings will be performed. Without a value, `path_validate` will
            detect the platform automatically.

    Raises:
        UnknownInodeError: the edited text contains an inode absent from the source text.
        TabulationError: a new name contains a tabulation. Although such a character is valid on most
            platforms, in the edited text it probably results from a typo.
        pathvalidate.ValidationError: a new name includes invalid character(s) for a filename
            (depends on the target platform).

    Returns:
        A list of clauses (path, new_name).
    """
    result = []
    for line in text.split("\n"):
        head, *tail = line.split("\t", maxsplit=1)
        if not tail:
            continue
        if not head.isdigit():
            continue
        inode = Inode(int(head))

        path = inodes_paths.get(inode)
        if path is None:
            raise UnknownInodeError(f"Unknown inode {inode}.")

        new_name = tail[0]
        if path.name == new_name:
            continue
        if new_name == "":
            raise EmptyNameError("A new name cannot be empty.")
        if "\t" in new_name:
            raise TabulationError(f"The new name '{new_name}' contains a tabulation.")
        try:
            pathvalidate.validate_filename(new_name, platform=platform or "auto")
        except pathvalidate.ValidationError:
            raise ValidationError(f"The new name '{new_name}' is invalid.")
        result.append(Clause(path, Name(new_name)))
    return result
