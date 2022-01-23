#! /bin/sh

REPO=# FILL ME 
WRAPPER=# FILL ME 
SRC=$REPO/src
BUNDLE=$REPO/app_bundle
PYTHON_SITE_PACKAGES=$(pip3 show pathvalidate | grep "^Location" | cut -c 11-)

if [ ! -d $REPO -o ! -d $SRC ]; then
    echo "FATAL ERROR: CHECK REPO'S PATH"
    exit 2
fi

if [ ! -d $BUNDLE ]; then
    mkdir $BUNDLE
fi

if [ ! -d $BUNDLE/src ]; then
    mkdir $BUNDLE/src
fi

if [ ! -d $BUNDLE/lib ]; then
    mkdir $BUNDLE/lib
fi

for package in $(ls $PYTHON_SITE_PACKAGES | egrep "(pathvalidate|natsort)"); do
    cp -Rf $PYTHON_SITE_PACKAGES/$package $BUNDLE/lib
done

for file in $(ls $SRC/*.py); do
    file=$(basename $file)
    if [ $file != "suprenam.py" -a $file != "__init__.py" ]; then
        cp -f $SRC/$file $BUNDLE/src/$file
    fi
done

cp -f $SRC/{suprenam.py,__init__.py} $REPO/LICENSE $BUNDLE
