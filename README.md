
<img align="left" width="120" src="/misc/logo.png">

## It's a bird... It's a plane...

It's **Suprenam**, a batch renaming utility which relies on the tool you know best: your text editor.

----

### Easy to use, but powerful

Suprenam is intended to sit in the **Finder toolbar**.

_To stick it there, press and hold <kbd>cmd</kbd> while dragging its icon to the desired location._

![Toolbar](/misc/toolbar.gif)

----

Afterwards, you can **drag and drop** items (any selection of files and folders) onto it.

![Drag and drop](/misc/drag_and_drop.gif)

----

Your favorite **text editor** will open with a list of names.
Make use of all your superpowers to modify them: multi-cursors, Find and Replace, regular expressions, you (re)name it.

![Edition](/misc/edition.gif)

When you're done, save and close.

----

The modifications are instantly applied on the selected items.

![Success](/misc/success.png)

Bam! Yet another achievement for Suprenam. 🎉

----

### Clever, reliable and fool-proof

Suprenam is not as straightforward as it seems. It supports:

- **Complex renamings.** As long as the desired final state is possible (e.g. no name clash), Suprenam will proceed. Under the hood, this may require it to go through intermediate names (e.g. for swapping `"foo.pdf"` and `"bar.pdf"`).
- **Rollback.** If something goes wrong during the actual process (e.g. a file is moved), don't worry: the work already completed will automatically be rolled back to the initial state.
- **Undo.** Likewise, you can always undo the previous renaming session. To that end, simply click the Suprenam icon without dropping anything on it.

----

## Installation

Currently, a single-file installation is available for macOS.


### Text Editor

#### MacOS

__Right click on a `.txt` file and select `Get Info`.__
> ![FileContextualMenuMac](/misc/right_click_contextual_menu_mac.png)

__Select your favorite text editor and click on the `Change All...` button.__
> ![GetInfoWindowMac](/misc/get_info_dialog_mac.png)
