
<img align="left" src="https://raw.githubusercontent.com/poponealex/suprenam/master/img/logo_small.png">

## It's a bird... It's a plane...

It's **Suprenam**, a batch renaming utility which relies on the tool you know best: your text editor.

----

### Sweet, but powerful

Suprenam sits in the Finder Toolbar, waiting for you to **drag and drop** any selection of files and folders onto it.

<p align="center"><img src="https://raw.githubusercontent.com/poponealex/suprenam/master/img/drag_and_drop.gif"></p>

----

Then, it will open your favorite **text editor** with a list of names.
Make use of all your superpowers to modify them: multi-cursors, Find and Replace, regular expressions, you (re)name it.

<p align="center"><img src="https://raw.githubusercontent.com/poponealex/suprenam/master/img/edition.gif"></p>

When you're done, save and close.

----

The modifications are instantly applied on the selected items.

<p align="center"><img src="https://raw.githubusercontent.com/poponealex/suprenam/master/img/success.png"></p>

Well, yet another achievement for Suprenam, I guess. 🎉

----

### Clever, reliable and fool-proof

Suprenam is not as straightforward as it seems. It supports:

- **Complex renamings.** As long as the desired final state is possible (e.g. no name clash), Suprenam will abide. Under the hood, this may require it to go through intermediate names (e.g. for swapping `"foo.pdf"` and `"bar.pdf"`).
- **Versioning.** When an item is tracked by git, Suprenam will use `git mv` to keep it under version control.
- **Rollback.** If something goes wrong during the actual process (e.g. a file is moved), don't worry: the work already completed will automatically be rolled back to the initial state.
- **Undo.** Likewise, you can always undo the previous renaming session. To that end, simply click the Suprenam icon without dropping anything on it.

----

## Installation

### Installing the app

#### MacOS

##### Retrieving or building the installer

- Download the latest installer from [Releases](https://github.com/poponealex/suprenam/releases) under the name `Suprenam.pkg`. It is unsigned: that means that you'll need to right-click or <kbd>ctrl</kbd>-click it and select “Open”.

- If you prefer to build it manually, follow [these instructions](build/platypus/instructions.md).

- In both cases, Suprenam requires Python 3.6 or later. You may have to [install it](https://www.python.org/downloads/).

##### Putting Suprenam in the Finder toolbar

- Press and hold <kbd>cmd</kbd> while dragging the Suprenam icon to the desired location.

<p align="center"><img src="https://raw.githubusercontent.com/poponealex/suprenam/master/img/toolbar.gif"></p>

##### Setting up your text editor (if needed)

If Suprenam insists to make you edit the names in TextEdit, don't let it ruin your life! Indeed, the TextEdit's associated command is currently unable to return when the file is closed, forcing you to quit it to proceed. This is a real pain in the OS, and we urge you to install and/or set as default a more capable text editor, for instance [Visual Studio Code](https://code.visualstudio.com/download). Assuming Suprenam knows how to deal with it, right-click on a `.tsv` file, press <kbd>alt</kbd>, and select it in `Always Open With`.

<p align="center"><img src="https://raw.githubusercontent.com/poponealex/suprenam/master/img/mac_set_default_text_editor.png"></p>

#### Linux

Coming soon.

#### Windows

Coming soon.

### Installing the command line tool

Although dragging and dropping the items to rename them is far more convenient, you can also launch Suprenam from the terminal. Install it with:

```
pip install suprenam
```

If this fails, try `pip3` instead of `pip`.

## How it works

- Being given a list of files and folders, Suprenam begins by retrieving their [**inodes**](https://en.wikipedia.org/wiki/Inode). These unique numeric identifiers will serve as an invariant throughout the renaming process.
- It creates a temporary text file associating each inode with its name. In case all items are siblings (i.e., have the same parent), the list is flat ; otherwise, a section is created for each parent.
- To find out how to open this file, Suprenam will use the following heuristics:
  - Retrieve the text editor that you have set as the default for opening TSV files.
  - If there is none, or Suprenam doesn't know the associated command, check for the presence of the ones that it actually supports, starting with VS-Code.
  - If this fails too, fall back to the default text editor of your operating system.
- Once the TSV file is opened, Suprenam waits for you to carry your modifications out.
- When the temporary file is closed, its content is parsed.
  - Suprenam ignores any change or deletion to non-inodes lines.
  - It  tolerates the deletion of one, several or even all of the inodes.
  - However, any inode creation or duplication is considered as a typo, and makes it to abort.
- The new names are checked for validity with respect to the actual file system.
- This results in a list of bindings between existing inodes and modified names. These bindings cannot be directly translated into renaming commands, as they may lead to name clashes.
  
  Below, for instance, `"c"` has two “target“ names, which will cause Suprenam to abort…

<p align="center"><img src="https://raw.githubusercontent.com/poponealex/suprenam/master/img/cycles_nope.png"></p>

  However, some desired bindings can be resolved along a “safe” path of renamings. For instance, the following renamings (from left to right: null, swapping, shifting, rolling) can always be obtained with careful intermediate renamings.

<p align="center"><img src="https://raw.githubusercontent.com/poponealex/suprenam/master/img/cycles_ok.png"></p>

  A handful of accepted and rejected renaming schemes are documented (and tested) [here](test/examples.md).  
- So, whenever possible, the desired bindings have been silently converted into a “safe” sequence. The new bindings are then processed in order, and the corresponding renaming commands executed. At this stage, the only remaining possible errors should result from hardware failures or from modifications that have occurred in the file tree during the edition stage. Should such rare cases arise, all the completed renaming commands will be readily rolled back.
- If your fate (or your footgun propensity) is relentless, and this fails too, the program will have no other choice but to leave the file system in a state which is neither the original nor the desired one. You should open the log file at `~/.suprenam/log.txt` to see what went wrong and what you can do about it.
- Suprenam can also use this log file to “undo” the previous renaming session by executing the sequence backwards. Obviously, a reversed sequence of safe renamings is still safe. Note, however, that a failed rollback cannot be automatically salvaged.

## Credits

- Authors: Aristide Grange and Alexandre Perlmutter.
- macOS GUI: [Platypus](https://github.com/sveinbjornt/Platypus), by Sveinbjorn Thordarson.
- Cross-plaform filename check: Python library [`pathvalidate`](https://github.com/thombashi/pathvalidate), by Tsuyoshi Hombashi.
- Natural sorting: Python library [`natsort`](https://github.com/SethMMorton/natsort), by Seth M. Morton.
