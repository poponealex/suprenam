import sys, os, re
from tempfile import NamedTemporaryFile
from pathlib import Path
from tkinter import messagebox
from collections.abc import Callable


class Color:
    FAIL = "\033[1;91m"
    INFO = "\033[1;94m"
    TITLE = "\033[1;96m"
    END = "\033[0m"


def main(
    strip_line: Callable = re.compile(r"#(\d+)#[ ]*([\w\W]+)").findall,
):
    if len(sys.argv) < 2:
        return
    population = {str(Path(x).stat().st_ino): Path(x) for x in sys.argv[1:]}
    temp_file = NamedTemporaryFile(mode="w+", delete=False)
    Path(temp_file.name).write_text("\n".join(f"#{inode}# {path.name}" for inode, path in population.items()))
    os.system(f"open {temp_file.name}")
    if messagebox.askokcancel("Confirm changes", "Rename the files?"):
        for line in Path(temp_file.name).read_text().split("\n"):
            try:
                inode, new_name = strip_line(line.strip())[0]
                file_path = population.get(inode)
            except:
                continue
            if file_path and file_path.name != new_name:
                file_path.rename(file_path.parent / new_name)
                print(f"{Color.TITLE}{file_path.name}{Color.INFO} renamed as {Color.TITLE}{new_name}{Color.END}")
    os.system(f"rm {temp_file.name}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"{Color.FAIL}{e}{Color.END}")
    sys.exit(0)