#! /bin/sh

APP=# FILL ME
LOG_DIR=$APP/Contents/Resources/.suprenam
LOG_FILE=$LOG_DIR/previous_session.log

if [ ! -d $LOG_DIR ]; then
    mkdir $LOG_DIR
fi

touch $LOG_FILE
sudo chmod g+rw $LOG_FILE
sudo chown root:staff $LOG_FILE
