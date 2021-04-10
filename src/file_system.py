from pathlib import Path
from bisect import bisect


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
        for candidate in self.as_list[bisect(self.as_list, parent):]:
            if not str(candidate).startswith(f"{parent}/"):
                break
            if candidate.match(f"{parent}/*") and candidate != path:
                yield candidate
