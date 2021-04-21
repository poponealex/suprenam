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
