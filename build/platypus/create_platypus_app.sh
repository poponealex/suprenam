#! /bin/sh

REPO_ABSOLUTE_PATH=# FILL ME
APP_DESTINATION=# FILL ME

WRAPPER="$REPO_ABSOLUTE_PATH/build/platypus/wrapper.sh"
SRC="$REPO_ABSOLUTE_PATH/src"
BUNDLE="$REPO_ABSOLUTE_PATH/build/platypus/app_bundle"
PYTHON_SITE_PACKAGES=$(pip3 show pathvalidate | grep "^Location" | cut -c 11-)
APP_VERSION="1.0.0"
PLATYPUS_SHARE="/usr/local/share/platypus"

if [ ! -d "$REPO_ABSOLUTE_PATH" -o ! -d "$SRC" ]; then
    echo "FATAL ERROR: CHECK REPO'S PATH"
    exit 2
fi

if [[ ! -d "$PLATYPUS_SHARE"  || ! -d "$PLATYPUS_SHARE/MainMenu.nib" || ! -f "$PLATYPUS_SHARE/ScriptExec" ]]; then
    echo "FIX YOUR PLATYPUS INSTALL"
    echo "Platypus share files ('MainMenu.nib' (dir) AND 'ScriptExec' (file)) have to be located at $PLATYPUS_SHARE"
    exit 2
fi

if [ ! -d "$BUNDLE" ]; then
    mkdir "$BUNDLE"
fi

if [ ! -d "$BUNDLE/src" ]; then
    mkdir "$BUNDLE/src"
fi

if [ ! -d "$BUNDLE/lib" ]; then
    mkdir "$BUNDLE/lib"
fi

for package in $(ls $PYTHON_SITE_PACKAGES | egrep "(pathvalidate|natsort)"); do
    cp -Rf "$PYTHON_SITE_PACKAGES/$package" "$BUNDLE/lib"
done

for file in $(ls $SRC/*.py); do
    file=$(basename $file)
    if [ "$file" != "suprenam.py" -a "$file" != "__init__.py" ]; then
        cp -f "$SRC/$file" "$BUNDLE/src/$file"
    fi
done

cp -f "$SRC"/{suprenam.py,__init__.py} "$REPO_ABSOLUTE_PATH/LICENSE" "$BUNDLE"

for file in $(ls $BUNDLE); do
    bundle_files="$bundle_files --bundled-file $BUNDLE/$file"
done

platypus \
--app-icon "/Applications/Platypus.app/Contents/Resources/PlatypusDefault.icns" \
--name "Suprenam" \
--interface-type "Text Window" \
--app-version "$APP_VERSION" \
--bundle-identifier "com.suprenam.Suprenam" \
--author "Aristide Grange & Alexandre Perlmutter" \
--interpreter '/bin/sh'  \
--uniform-type-identifiers 'public.item|public.folder' \
$bundle_files \
--droppable \
--optimize-nib \
--overwrite \
"$WRAPPER" \
"$APP_DESTINATION/Suprenam.app"

rm -rf "$BUNDLE"
exit
