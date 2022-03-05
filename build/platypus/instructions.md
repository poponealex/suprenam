# Suprenam macOS app deployment procedure

## Requirements

### Download Packages 

> http://s.sudre.free.fr/Software/Packages/about.html

### Required command line tools

- `pip` or `pip3`
- `platypus`

### Required Python Packages

- `pathvalidate`
- `natsort`

## Create the App and the Package - `build.sh` 

- Run `chmod +x build/platypus/build.sh` from **repo's root**.
- Run `build/platypus/build.sh` from **repo's root**.
- The app will be located at `build/platypus/Suprenam.app`
- The package will be located at `build/platypus/Suprenam.pkg`

#### Current App settings

- App Name: `Suprenam`
- Icon: cf. `build/logo.icns`
- Version: `1.0.0 (as of 24/01/2022)`
- Author: `Aristide Grange & Alexandre Perlmutter`
- Bundle Identifier: `com.suprenam.Suprenam`
- Script Path: `build/platypus/wrapper.sh`
- Interface: `Text Window`
- uniform-type-identifiers: `public.item|public.folder`
