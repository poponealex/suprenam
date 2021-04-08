from pathlib import Path

ROOT = "FHS"
PATHS = Path("fhs.txt").read_text().split("\n")[:-1]

def create_fhs():
    if not Path(ROOT).exists():
        Path(ROOT).mkdir()
        for path in PATHS:
            Path(f"{ROOT}{path}").mkdir()
