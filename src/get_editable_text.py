from itertools import groupby

from src.goodies import remove_diacritics, string_to_pairs
from src.user_types import EditableText, InodesPaths


def get_editable_text(inodes_paths: InodesPaths) -> EditableText:
    """
    Being given a mapping of inodes (ints) to paths (Path objects), return a textual representation
    of these associations, sorted in natural order and grouped by common parent if needed.

    Args:
        inodes_paths: dict of { inode: path }

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
    # Calculate the number of digits in the largest inode (base 10), or 0 if there are no inodes
    inode_size = len(str(max(inodes_paths.keys(), default=0)))

    # Create a naturally sorted list of triples (parent, name, inode) with null paths filtered out
    parents_names_inodes = sorted(
        [  # natural sort by parent, then name, then (useless) inode
            (
                f"\n{path.parent}",  # the prefix '\n' adds an empty line for maximal consistency
                path.name,
                str(inode).zfill(inode_size),
            )
            for (inode, path) in inodes_paths.items()
            if path.name  # null paths (empty or root) would make os_sorted raise a ValueError
        ],
        key=lambda triple: (string_to_pairs(remove_diacritics(f"{triple[0]} {triple[1]}"))),
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
        result.append("")
    return EditableText("\n".join(result))
