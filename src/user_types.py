from pathlib import Path
from typing import Dict, Literal, NamedTuple, NewType

Name = NewType("Name", str)


class Clause(NamedTuple):
    path: Path
    new_name: Name


ClauseMap = Dict[Path, Name]


class Renaming(NamedTuple):
    source: Path
    target: Path


Inode = NewType("Inode", int)

InodePaths = Dict[Inode, Path]

EditableText = NewType("EditableText", str)
EditedText = NewType("EditedText", str)
