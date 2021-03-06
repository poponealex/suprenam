#! /bin/sh

export PATH="/usr/local/bin:$PATH"
export PYTHONPATH="lib"
TEMP_FILE="/tmp/suprenam_paths.txt"

python_command=python3
if ! command -v python3 &> /dev/null; then # https://stackoverflow.com/questions/592620/how-can-i-check-if-a-program-exists-from-a-bash-script/677212#677212
    python_command=python
fi

# Launch Python to get the version of Python, and concatenate its two parts
# (major and minor) on 4 digits (e.g. 3.6 -> "0306") for easier comparison.
# This should work up to Python 99.99, which ought to be enough for anybody.
if [[ `$python_command -c "import sys; print('{0[0]:02}{0[1]:02}'.format(sys.version_info))"` < "0306" ]]; then
    echo "ALERT:Fatal error|Python 3.6 or higher is required. Yours is `$python_command --version | cut -f 2`."
    exit 2
fi

if [ $# -gt 0 ]; then
    $python_command suprenam.py "$@"
else
    if [ -e ~/Library/Application\ Support/Suprenam/log.txt ]; then
        $python_command suprenam.py
    else
        echo "ALERT:Usage|"`
            `"Drag and drop onto the Suprenam's icon a bunch of items you want to rename. "`
            `"Clicking the icon will be used to undo the previous renaming session (if any)."
        exit 2
    fi
fi
