from typing import List

import pathvalidate

from src.goodies import print_fail
from src.user_errors import *
from src.user_types import Clause, EditedText, Inode, InodesPaths, Name


def parse_edited_text(
    text: EditedText,
    inodes_paths: InodesPaths,
    platform: str = "auto",  # enable testing on different platforms
) -> List[Clause]:
    """
    Parse the renamings' text.

    Args:
        text: the text with the effective renamings.
        inodes_paths: dict containing each path (value) with its inode (key).
        platform: OS on which the renamings will be performed. The default "auto" means that the
            platform will be detected automatically.

    Raises:
        UnknownInodeError: the edited text contains an inode absent from the source text.
        TabulationError: a new name contains a tabulation. Although such a character is valid on most
            platforms, in the edited text it probably results from a typo.
        pathvalidate.ValidationError: a new name includes invalid character(s) for a filename
            (depends on the target platform).

    Returns:
        A list of Clause (path, new_name).
    """
    result = []
    seen_inodes = set()
    for line in text.split("\n"):
        head, *tail = line.split("\t", maxsplit=1)
        if not tail:
            continue
        if not head.isdigit():
            continue

        inode = Inode(int(head))
        if inode not in seen_inodes:
            seen_inodes.add(inode)
        else:
            print_fail(f"Several targets for inode {inode}.")
            raise SeveralTargetsError
        
        path = inodes_paths.get(inode)
        if path is None:
            print_fail(f"Unknown inode {inode}.")
            raise UnknownInodeError
        
        new_name = tail[0]
        if "\t" in new_name:
            print_fail(f"Illegal tabulation in the new name: {repr(new_name)}.")
            raise TabulationError
        if path.name == new_name:
            continue
        try:
            pathvalidate.validate_filename(new_name, platform=platform)
        except pathvalidate.ValidationError:
            print_fail(f"Invalid character(s) in the new name: {repr(new_name)}.")
            raise ValidationError
        result.append(Clause(path, Name(new_name)))
    return result
