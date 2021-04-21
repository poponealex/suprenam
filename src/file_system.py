from pathlib import Path
from hashlib import sha256
from itertools import count


class FileSystem(set):
    
    def children(self, path):
        for candidate in self:
            if candidate.match(f"{path}/*"):
                yield candidate

    def siblings(self, path):
        for candidate in self.children(path.parent):
            if path != candidate:
                yield candidate

    def non_existing_sibling(self, path):
        """Calculate the path of a non-existing sibling of a given path."""
        digest = sha256(path.stem.encode("utf8")).hexdigest()[:32]
        for suffix in count():
            new_path = path.with_stem(f"{digest}-{suffix}")
            if new_path not in self:
                return new_path
    
    def rename(self, path, new_path):
        """
        Rename a path into a new path, assuming the following preconditions:

        1. `path` and `new_path` are siblings
        2. `path` is in the file system
        3. `new_path` is not yet in the file system

        Results:
            - `path` is replaced by `new_path` in the file system
            - any descendant of `path` is replaced by the appropriate `path`
        
        Note:
            When working on a virtual file system, renaming a node before its
            parent is not mandatory.
        """
        offset = len(str(path)) + 1
        for candidate in list(self):
            if candidate == path or str(candidate).startswith(f"{path}/"):
                self.remove(candidate)
                self.add(new_path / str(candidate)[offset:])
