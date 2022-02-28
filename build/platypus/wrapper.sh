#! /bin/sh

export PATH="/usr/local/bin:$PATH"
export PYTHONPATH="lib"
TEMP_FILE="/tmp/suprenam_paths.txt"

python_command=python3
if ! command -v python3 &> /dev/null; then # https://stackoverflow.com/questions/592620/how-can-i-check-if-a-program-exists-from-a-bash-script/677212#677212
    python_command=python
fi

if ! [[ `$python_command --version | cut -f 2` > "3.6" ]]; then
    echo "Python 3.6+ is required."
    exit 2
fi

while [ $# -gt 0 ]; do
    echo $1 >> "$TEMP_FILE"
    shift
done

if [ -f "$TEMP_FILE" ]; then
    $python_command suprenam.py -f "$TEMP_FILE"
    rm -f "$TEMP_FILE"
fi
