# Suprenam macOS app deployment procedure

## Create the app bundle

## Required command line tools

- `pip3`
- `platypus`

### Required Python Packages

- `pathvalidate`
- `natsort`

### Automatized creation of the Platypus app - `create_platypus_app.sh`

- Instantiate `REPO_ABSOLUTE_PATH` variable with suprenam's repo's absolute path in `build/platypus/create_platypus_app.sh`.
- Instantiate `APP_DESTINATION` with the app's destination **directory**'s absolute path.
- Run `chmod +x build/platypus/create_platypus_app.sh` from repo's root.
- Run `./build/platypus/create_platypus_app.sh` from repo's root.

#### Current App settings

- App Name: `Suprenam`
- Icon: `**TODO**`
- Version: `1.0.0 (as of 24/01/2022)`
- Author: `Aristide Grange & Alexandre Perlmutter`
- Bundle Identifier: `com.suprenam.Suprenam`
- Script Path: `build/platypus/wrapper.sh`
- Interface: `Text Window`
- uniform-type-identifiers: `public.item|public.folder`


## Create a package

### Download Packages 

> http://s.sudre.free.fr/Software/Packages/about.html

### Create a new Distribution project

#### Project Tab Settings

- Name: Suprenam
- Path: `build` (build directory's path)
- Format: `Flat`

<img width="1312" alt="screenshot 2021-10-07 at 4 18 21 PM" src="https://user-images.githubusercontent.com/74072635/136407528-a2d763f9-6e17-422a-b003-b0ac6edd2546.png">

#### Suprenam package Tab

##### Settings Tab

- Identifier: com.suprenam.Suprenam
- Version: 1.0.0 (as of 07/10/2021)

<img width="1312" alt="screenshot 2021-10-07 at 4 19 17 PM" src="https://user-images.githubusercontent.com/74072635/136407747-386af7ce-4520-4fb5-81c8-7183d1e830cd.png">

##### Payload Tab

- Drag and drop `Supernam.app` under `Applications` in **Contents**
- Set the user's privileges as root:staff
- See the screenshot below for the the read/write/execute permissions

<img width="1312" alt="screenshot 2021-10-07 at 4 19 34 PM" src="https://user-images.githubusercontent.com/74072635/136408097-b80b5d7a-d2e4-43ee-9c1d-3e0e96be3998.png">

### Build with cmd+B or click Build->Build in the toolbar.

> The package will be built in BUILD_FOLDER/build.
