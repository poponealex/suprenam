__import__("sys").path[0:0] = ["."]
import subprocess
from pathlib import Path
from bisect import bisect, insort
from hashlib import sha256
from itertools import count


class FileSystem:
    def __init__(self, path_strings, is_pure=False, skip_git=False):
        if is_pure:
            self.as_set = set(map(Path, path_strings))
            self.as_population = {str(i): Path(path) for i, path in enumerate(path_strings)}
            self.rename = self.rename_pure
        else:
            self.rename = self.rename_system
            self.as_set = set()
            self.as_population = {}
            self.git = set()
            for path_string in path_strings:
                path = Path(path_string).resolve()
                self.as_population[str(path.stat().st_ino)] = path
                if path not in self.as_set:
                    self.as_set.update(path.parent.glob("*"))
        self.as_list = sorted(self.as_set)

    def exists(self, path):
        return path in self.as_set

    def index(self, path):
        """Return the index at/after which the given path is/should be stored."""
        return bisect(self.as_list, path)

    def children(self, path):
        for candidate in self.as_list[self.index(path) :]:
            if not str(candidate).startswith(f"{path}/"):
                break
            if candidate.match(f"{path}/*"):
                yield candidate

    def siblings(self, path):
        for candidate in self.children(path.parent):
            if path != candidate:
                yield candidate

    def add(self, path):
        insort(self.as_list, path)
        self.as_set.add(path)

    def remove(self, path):
        if self.exists(path):
            index = self.index(path)
            if self.as_list[index] != path:
                index -= 1
            del self.as_list[index]
            self.as_set.remove(path)

    def uncollide(self, path):
        """Calculate and add a non-colliding new name for path."""
        digest = sha256(path.stem.encode("utf8")).hexdigest()
        for suffix in count():
            new_path = path.with_stem(f"{digest}-{suffix}")
            if not self.exists(new_path):
                self.add(new_path)
                return new_path

    def rename_pure(self, original_path, new_path):
        """Virtually rename a path in the FileSystem object's as_set and as_list instances."""
        for path in self.children(original_path):
            self.remove(path)
            self.add(Path(new_path / path.name))
        self.remove(original_path)
        self.add(new_path)

    def rename_system(self, original_path, new_path):
        try:
            subprocess.run(
                ["git", "mv", original_path.name, new_path.name],
                cwd=original_path.parent,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            ).check_returncode()
        except subprocess.CalledProcessError:
            original_path.rename(new_path)
