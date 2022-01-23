# Suprenam macOS app deployment procedure

## Create the app bundle

### Required Python Packages

- pathvalidate
- natsort

### `create_macOS_bundle.sh` script

- Instantiate `REPO` variable with suprenam's repo's path.
- Instantiate `WRAPPER` variable with `wrapper.sh`'s path.
- Run `chmod +x create_macOS_bundle.sh`.
- Run `./create_macOS_bundle.sh`

## Create the app with Platypus

### Settings

- App Name: Suprenam
- Icon: **TODO**
- Version: 1.0.0 (as of 07/10/2021)
- Author: Aristide Grange & Alexandre Perlmutter
- Identifier: com.suprenam.Suprenam
- Script Type: Shell (`/bin/sh`)
- Script Path: Path to `wrapper.sh`
- Interface: Text Window
- Check *Accept dropped items*
- Accept dropped items settings: Check *Accept dropped files*
- Bundle Files: Select all the files and folders from the `app_bundle` folder created by `create_macOS_bundle.sh` (except `wrapper.sh`).

<img width="776" alt="screenshot 2021-10-07 at 4 06 05 PM" src="https://user-images.githubusercontent.com/74072635/136402953-a62e8ff9-b47d-4677-9c95-98265a39863e.png">
<img width="912" alt="screenshot 2021-10-07 at 3 47 44 PM" src="https://user-images.githubusercontent.com/74072635/136402966-204e1288-d05c-45b4-9ca9-b6e75ed3d7b5.png">
<img width="776" alt="screenshot 2021-10-07 at 3 47 22 PM" src="https://user-images.githubusercontent.com/74072635/136402979-02a68ed7-d7ff-437f-aa4d-bf3cb5f5193b.png">


- Click <kbd>Create App</kbd>
- Instantiate `APP` variable in `create_log_macOS_app.sh` with the App's path
- Run `chmod a+x create_log_macOS_app.sh`
- Run `sudo ./create_log_macOS_app.sh`

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
