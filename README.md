
<img align="left" src="/img/logo_small.png">

## It's a bird... It's a plane...

It's **Suprenam**, a batch renaming utility which relies on the tool you know best: your text editor.

----

### Sweet, but powerful

Suprenam sits in the Finder Toolbar, waiting for you to **drag and drop** any selection of files and folders onto it.

<p align="center"><img src="/img/drag_and_drop.gif"></p>

----

Then, it will open your favorite **text editor** with a list of names.
Make use of all your superpowers to modify them: multi-cursors, Find and Replace, regular expressions, you (re)name it.

<p align="center"><img src="/img/edition.gif"></p>

When you're done, save and close.

----

The modifications are instantly applied on the selected items.

<p align="center"><img src="/img/success.png"></p>

Well, yet another achievement for Suprenam, I guess. 🎉

----

### Clever, reliable and fool-proof

Suprenam is not as straightforward as it seems. It supports:

- **Complex renamings.** As long as the desired final state is possible (e.g. no name clash), Suprenam will proceed. Under the hood, this may require it to go through intermediate names (e.g. for swapping `"foo.pdf"` and `"bar.pdf"`).
- **Rollback.** If something goes wrong during the actual process (e.g. a file is moved), don't worry: the work already completed will automatically be rolled back to the initial state.
- **Undo.** Likewise, you can always undo the previous renaming session. To that end, simply click the Suprenam icon without dropping anything on it.

----

## Installation (GUI)

### MacOS

#### Installing Suprenam

TODO.

#### Putting Suprenam in the Finder toolbar

<p align="center"><img src="/img/toolbar.gif"></p>

Press and hold <kbd>cmd</kbd> while dragging the Suprenam icon to the desired location.

#### Setting up your default text editor (if needed)

By default, Suprenam will fall back on TextEdit, which is currently not able to send a signal when an editing window is closed, forcing you to quit it to proceed. This is a major annoyance, and we recommend you to set a more capable Text Editor as default.

To this end, right click on a `.txt` file and select `Get Info`. In the Info window, select your favorite text editor and click on the `Change All...` button.

<p align="center"><img src="/img/mac_set_default_text_editor.png"></p>


### Linux

TODO.

### Windows

## Installation (command line)

## How it works

- Being given a list of files and folders, Suprenam begins by retrieving their [**inodes**](https://en.wikipedia.org/wiki/Inode). These unique numeric identifiers will serve as an invariant throughout the renaming process.
- It creates a temporary text file associating each inode with its name. In case all items are siblings (i.e., have the same parent), the list is flat ; otherwise, a section is created for each parent.
- Suprenam opens this list in a text editor, and waits for you to carry out your modifications.
- When the temporary file is closed, its content is parsed.
  - Suprenam ignores any change or deletion to non-inodes lines.
  - It  tolerates the deletion of one, several or even all ot the inodes.
  - However, any inode creation or duplication is considered as a typo, and makes it to abort.
- The new names are checked for validity with respect to the actual file system (courtesy of the [`pathvalidate`](https://github.com/thombashi/pathvalidate) package).
- This results in a list of bindings between existing inodes and modified names. These bindings cannot be directly translated into renaming commands, as they may lead to name clashes.
  
  Below, for instance, `"c"` has two “target“ names, which will cause Suprenam to abort…

  <p align="center"><img src="/img/cycles_nope.png"></p>

  However, some desired bindings can be resolved along a “safe” path of renamings. For instance, the following renamings (from left to right: null, swapping, shifting, rolling) can always be obtained with careful intermediate renamings.

  <p align="center"><img src="/img/cycles_ok.png"></p>

  A lot of accepted and rejected renaming schemes are documented (and tested) [here](test/examples.md).  
- So, whenever possible, the desired bindings have been silently converted into a “safe” sequence. The new bindings are then processed in order, and the corresponding renaming commands executed. At this stage, the only remaining possible errors should result from hardware failures or from modifications that have occurred in the file tree during the edition stage. Should such rare cases arise, all the completed renaming commands will be readily rolled back.
- If your fate (or your footgun propensity) is relentless, and this fails too, the program will have no other choice but to leave the file system in a state which is neither the original nor the desired one. You should open the log file at `~/.suprenam/log.txt` to see what went wrong and what you can do about it.
- Suprenam can also use this log file to “undo” the previous renaming session by executing the sequence backwards. Obviously, a reversed sequence of safe renamings is still safe. Note, however, that a failed rollback cannot be automatically salvaged.
