#! /bin/sh

export PATH="/usr/local/bin:$PATH"
export PYTHONPATH="lib"
TEMP_FILE="/tmp/suprenam_paths.txt"

while [ $# -gt 0 ]; do
    echo $1 >> $TEMP_FILE
    shift
done

if [ -f $TEMP_FILE ]; then
    python3 suprenam.py -f $TEMP_FILE
    rm -f $TEMP_FILE
fi
