import subprocess
import sys
from pathlib import Path

sys.path[0:0] = ["."]

from src.goodies import rm_tree
from src.logger import logger
from src.suprenam import run_on_path_list
from src.renamings import Renamer


playground = Path("test/playground")
paths = [
    playground / "a/aa/aaa",
    playground / "a/aa/aaa",
    playground / "a/aa/aab",
    playground / "a/aa/aac",
    playground / "a/ab/aba",
    playground / "a/ab/abb",
    playground / "a/ab/abc",
    playground / "a/ac/aca",
    playground / "a/ac/acb",
    playground / "a/ac/acc",
    playground / "b/ba/bab",
    playground / "b/ba/bac",
    playground / "b/bb/bba",
    playground / "b/bb/bbb",
    playground / "b/bb/bbc",
    playground / "a/aa",
    playground / "a/ab",
    playground / "a",
    playground / "b/ba",
]


rm_tree(playground)
for path in paths:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.touch()

print("Playground recreated. Now, have fun renaming some files and folders...")
logger.create_new_log_file()
run_on_path_list(paths)

renamer = Renamer()

input("Press Enter to show the log file...")
print(logger.get_contents())

input("Press Enter to revert the previous renamings...")
arcs_for_undoing = renamer.get_arcs_for_undoing(logger.get_contents())
renamer.perform_renamings(arcs_for_undoing)

input("Press Enter to show the log file...")
print(logger.get_contents())

input("Press Enter to erase the playground...")
rm_tree(playground)
