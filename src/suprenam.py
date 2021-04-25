from pathlib import Path
import subprocess
import sys
from tempfile import NamedTemporaryFile


def main():
    temporary_file = Path(NamedTemporaryFile(mode="w", delete=False, suffix=".txt").name)
    temporary_file.write_text("\n".join(sys.argv[1:]))
    subprocess.check_output(["/usr/local/bin/code", "-w", temporary_file])
    result = temporary_file.read_text()
    print(result)


if __name__ == "__main__":
    if len(sys.argv) >= 2:
        sys.exit(main())
