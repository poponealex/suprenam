#! /bin/sh

if ! command -v platypus &> /dev/null; then
    echo "Install Platypus! -> brew install platypus"
    exit 2
fi

if ! command -v packagesbuild &> /dev/null; then
    echo "Install Packages! -> http://s.sudre.free.fr/Software/Packages/about.html"
    exit 2
fi

python_command=python3
echo "Select python3 as python command"
if ! command -v python3 &> /dev/null; then
    echo "python3 not found: fall back on python"
    python_command=python
fi

BUILD="build/platypus"
WRAPPER="$BUILD/wrapper.sh"
SRC="src"
BUNDLE="$BUILD/app_bundle"
PYTHON_SITE_PACKAGES=$($python_command -c "import site; print(site.getsitepackages()[0])")
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
    read -p "$BUNDLE : This has nothing to do here, confirm deletion (y) " del \
    && [[ $del != [yY] ]] \
    && echo "Move or delete $BUNDLE, then try again" \
    && exit 2

    rm -rf "$BUNDLE"
fi

mkdir "$BUNDLE" "$BUNDLE"/{src,lib}

cp -Rf "$PYTHON_SITE_PACKAGES/pathvalidate" "$BUNDLE/lib"
cp -Rf "$PYTHON_SITE_PACKAGES/natsort" "$BUNDLE/lib"

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
--app-icon "$BUILD/../logo.icns" \
--name "Suprenam" \
--interface-type "None" \
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
"$APP_DESTINATION" \
&& echo "\nAPP -> $APP_DESTINATION\n" \
&& packagesbuild --build-folder "`pwd`/$BUILD" --package-version "$APP_VERSION" "$PKG_PROJECT" \
&& echo "\nPKG -> $PKG_DESTINATION"

rm -rf "$BUNDLE"

exit
