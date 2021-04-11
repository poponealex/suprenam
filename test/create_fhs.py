__import__("sys").path[0:0] = ["."]
from pathlib import Path


PATHS = Path("test/fhs.txt").read_text().split("\n")[:-1]


def create_fhs(root="test/FHS"):
    if not Path(root).exists():
        Path(root).mkdir()
        for path in PATHS:
            Path(f"{root}{path}").mkdir()
