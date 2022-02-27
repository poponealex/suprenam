#! /bin/sh

export PATH="/usr/local/bin:$PATH"
export PYTHONPATH="lib"
TEMP_FILE="/tmp/suprenam_paths.txt"

findPythonBin (){
    for i in {6..10}; do
        if command -v python3.$i &> /dev/null; then 
            python_command=python3.$i
            return
        fi
    done
    echo "Python 3.6+ is required."
    exit 2
}

python_command=python3
if ! command -v python3 &> /dev/null; then
    python_command=python
fi

isValidPythonVersion=`$python_command --version | awk '{
    split($2, res, ".");
    print (res[1] < 3 || res[2] < 6) ? 0 : 1;
    delete res;
}'`

if [[ ! $isValidPythonVersion == "1" ]]; then
    findPythonBin
fi

while [ $# -gt 0 ]; do
    echo $1 >> "$TEMP_FILE"
    shift
done

if [ -f "$TEMP_FILE" ]; then
    $python_command suprenam.py -f "$TEMP_FILE"
    rm -f "$TEMP_FILE"
fi
