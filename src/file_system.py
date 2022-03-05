from base64 import b32encode
from itertools import count
from pathlib import Path
from typing import Generator, Iterable, Optional, Set

from pathvalidate import validate_filename


class FileSystem(set):
    def __init__(self, paths: Optional[Iterable[Path]] = None, platform: Optional[str] = None):
        if paths:  # when some initial paths are provided, the file system is considered as pure
            super().__init__(paths)
            for path in self:
                validate_filename(
                    path.name,
                    platform=platform or "auto",
                )  # validate each filename when working with a pure FileSystem
            self.path_exists = lambda path: path in self
            self.siblings = lambda path: self.children(path.parent)
        else:  # otherwise, the file system is considered as concrete
            super().__init__()
            self.path_exists = lambda path: path.exists()
            self.siblings = lambda path: path.parent.glob("*")

    def update_with_source_paths(self, source_paths: Iterable[Path]) -> None:
        """Check all paths exist in the file system and "close" it with their siblings.

        Args:
            source_paths (Iterable[Path]): the paths to be renamed.

        Raises:
            FileNotFoundError: a source path is absent from the file system.
        """
        result: Set[Path] = set()
        for source_path in source_paths:
            if not self.path_exists(source_path):
                raise FileNotFoundError(source_path)
            result.update(self.siblings(source_path))
        self.update(result)  # should not change a pure file system

    def children(self, path: Path) -> Generator[Path, None, None]:
        for candidate in self:
            if candidate.match(f"{path}/*"):
                yield candidate

    def non_existing_sibling(self, path: Path) -> Path:
        """Create the path of a non-existing sibling of a given path.

        Args:
            path (Path): a source path which is the target of another renaming.

        Returns:
            Path: the path to be temporarily used for an intermediate renaming.

        Notes:
            - A previous version relied on `Path.with_stem`, which requires Python 3.9. In the
            present version, the non existing sibling does not conserve the extension of the
            original file.
            - Truncated SHA-256 and BASE-64 were considered, but the former is overkill, and the
            character set of the latter is not appropriate for filenames.
        """
        digest = b32encode(path.name.encode("utf8")).decode("ascii")[:32]
        for suffix in count():
            new_path = path.with_name(f"{digest}-{suffix}")
            if new_path not in self:
                break
        return new_path

    def rename(self, path, new_path):
        """Rename a path into a new path, and rename recursively its descendants.

        The following preconditions are normally satisfied:

        1. `path` and `new_path` are siblings,
        2. `path` is in the file system,
        3. and `new_path` is not in the file system yet.

        Results:
            - `path` is replaced by `new_path` in the file system.
            - Any descendant of `path` is replaced by the appropriate `path`.

        Notes:
            - The renaming is virtual only. The ultimate goal is to produce a sequence of "safe"
                clauses (or arcs) for an ulterior actual renaming.
                Nevertheless, all the consequences of a renaming (specifically, of a folder) are
                simulated to ensure testability.
            - In a virtual file system, renaming a node before its parent is not mandatory.
        """
        offset = len(str(path)) + 1
        for candidate in list(self):
            if candidate == path or str(candidate).startswith(f"{path}/"):
                self.remove(candidate)
                self.add(new_path / str(candidate)[offset:])
