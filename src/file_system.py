from pathlib import Path
from bisect import bisect, insort
from hashlib import sha256
from itertools import count


class FileSystem:
    def __init__(self, path_strings, is_pure=False):
        if is_pure:
            self.as_set = set(map(Path, path_strings))
        else:
            self.as_set = set()
            for path_string in path_strings:
                path = Path(path_string)
                if path in self.as_set:
                    continue
                if not path.exists():
                    raise FileNotFoundError
                self.as_set.update(path.parent.glob("*"))
        self.as_list = sorted(self.as_set)

    def exists(self, path):
        return path in self.as_set

    def siblings(self, path):
        parent = path.parent
        for candidate in self.as_list[bisect(self.as_list, parent) :]:
            if not str(candidate).startswith(f"{parent}/"):
                break
            if candidate.match(f"{parent}/*") and candidate != path:
                yield candidate

    def add(self, path):
        insort(self.as_list, path)
        self.as_set.add(path)

    def uncollide(self, path):
        """Calculate and add to the file system a non-colliding new name for path."""
        digest = sha256(path.stem.encode("utf8")).hexdigest()
        for suffix in count():
            new_path = path.with_stem(f"{digest}-{suffix}")
            if not self.exists(new_path):
                self.add(new_path)
                return new_path
