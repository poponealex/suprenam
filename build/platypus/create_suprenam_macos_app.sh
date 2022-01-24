#! /bin/sh

pip_command=pip3
if ! command -v pip3 &> /dev/null; then
    pip_command=pip
fi

BUILD="build/platypus"
WRAPPER="$BUILD/wrapper.sh"
SRC="src"
BUNDLE="$BUILD/app_bundle"
PYTHON_SITE_PACKAGES=$($pip_command show pathvalidate | grep "^Location" | cut -c 11-)
PLATYPUS_SHARE="/usr/local/share/platypus"
APP_DESTINATION="$BUILD/Suprenam.app"
APP_VERSION="1.0.0"
PKG_PROJECT="$BUILD/Suprenam.pkgproj"
PKG_DESTINATION="$BUILD/Suprenam.pkg"

if [[ ! -d "$SRC" || ! -d "$BUILD" ]]; then
    echo "FATAL ERROR: check that you're at the Suprenam's root"
    echo "currently located at: `pwd`"
    exit 2
fi

if [[ ! -d "$PLATYPUS_SHARE"  || ! -d "$PLATYPUS_SHARE/MainMenu.nib" || ! -f "$PLATYPUS_SHARE/ScriptExec" ]]; then
    echo "FIX YOUR PLATYPUS INSTALL"
    echo "Platypus share files ('MainMenu.nib' (dir) AND 'ScriptExec' (file)) have to be located at $PLATYPUS_SHARE"
    exit 2
fi

if [ -e "$BUNDLE" ]; then
    read -p "$BUNDLE : This has nothing to do here, confirm deletion (y) " del && [[ $del != [yY] ]] && echo "Move or delete $BUNDLE, then try again" && exit 2
    rm -rf "$BUNDLE"
fi

mkdir "$BUNDLE" "$BUNDLE"/{src,lib}

for package in $(ls $PYTHON_SITE_PACKAGES | egrep "(pathvalidate|natsort)"); do
    cp -Rf "$PYTHON_SITE_PACKAGES/$package" "$BUNDLE/lib"
done

for file in $(ls $SRC/*.py); do
    file=$(basename $file)
    if [ "$file" != "suprenam.py" -a "$file" != "__init__.py" ]; then
        cp -f "$SRC/$file" "$BUNDLE/src/$file"
    fi
done

cp -f "$SRC"/{suprenam.py,__init__.py} "LICENSE" "$BUNDLE"

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
--interpreter "/bin/sh"  \
--uniform-type-identifiers "public.item|public.folder" \
$bundle_files \
--droppable \
--optimize-nib \
--overwrite \
"$WRAPPER" \
"$APP_DESTINATION"

packagesbuild --build-folder "`pwd`/$BUILD" --package-version "$APP_VERSION" "$PKG_PROJECT"

rm -rf "$BUNDLE"

echo
echo "APP -> $APP_DESTINATION"
echo "PKG -> $PKG_DESTINATION"

exit