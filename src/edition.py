from pathlib import Path
from typing import List


def edit_paths(
    paths: List[Path],
    get_inode=lambda path: path.stat().st_ino,  # enable testing with a fake (pure) inode getter
    get_edition_handler=get_editable_file_path, # enable testing with a pure function returning a text
    edit=run_editor, # enable simulating the user's editions
):
    inode_paths = {get_inode(path): path for path in paths}
    handler = get_edition_handler(inode_paths)
    text = edit(handler)
    clauses = parse_edited_text(text, inode_paths)
    return clauses


