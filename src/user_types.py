from pathlib import Path
from typing import Dict, NamedTuple, NewType

Name = NewType("Name", str)


class Clause(NamedTuple):
    path: Path
    new_name: Name


ClauseMap = Dict[Path, Name]


class Arc(NamedTuple):
    source: Path
    target: Path


Inode = NewType("Inode", int)

InodesPaths = Dict[Inode, Path]

EditableText = NewType("EditableText", str)
EditedText = NewType("EditedText", str)
