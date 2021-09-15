from pathlib import Path
from typing import List
from itertools import groupby
from tempfile import NamedTemporaryFile


def get_editable_text(inode_paths):
    result = []
    print(list(inode_paths.items()))
    paths_and_inodes = sorted(
        ((path, inode) for (inode, path) in inode_paths.items()),
        key=lambda x: (x[0].parent, x[0].name), # sorted by parent, then by name
    )
    for (parent, children) in groupby(paths_and_inodes, key=lambda item: item[0].parent):
        result.append(f"{parent}")
        for (path, inode) in children:
            result.append(f"{inode}\t{path.name}")
        result.append("")
    return "\n".join(result)


def get_editable_file_path(inode_paths):
    path = Path(NamedTemporaryFile(mode="w+", delete=False, suffix=".txt"))
    path.write_text(get_editable_text(inode_paths))
    return path


def run_editor(editable_file_path: Path) -> str:
    pass


def parse_edited_text(text, inode_paths):
    pass


def edit_paths(
    paths: List[Path],
    get_inode=lambda path: path.stat().st_ino,  # enable testing with a fake (pure) inode getter
    get_edition_handler=get_editable_file_path,  # enable testing with a pure function returning a text
    edit=run_editor,  # enable simulating the user's editions
):
    inode_paths = {get_inode(path): path for path in paths}
    handler = get_edition_handler(inode_paths)
    text = edit(handler)
    clauses = parse_edited_text(text, inode_paths)
    return clauses
