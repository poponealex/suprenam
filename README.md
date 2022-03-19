
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

----

### Clever, reliable and fool-proof

Suprenam is not as straightforward as it seems. It supports:

- **Complex renamings.** As long as the desired final state is possible (e.g. no name clash), Suprenam will abide. Under the hood, this may require it to go through intermediate names (e.g. for swapping `"foo.pdf"` and `"bar.pdf"`).
- <img align="right" src="https://raw.githubusercontent.com/poponealex/suprenam/master/img/thank_you.png">**Versioning.** When an item is tracked by git, Suprenam will use `git mv` to keep it under version control.
  
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

#### Linux and Windows

No graphical launcher yet. Use the command line tool.

### Installing the command line tool

Although dragging and dropping the items to rename them is far more convenient, you can also launch Suprenam from the terminal. Install it with:

```
pip install suprenam
```

If this fails, try `pip3` instead of `pip`.

### Configuring Suprenam

On first launch, Suprenam creates a workspace at:
- `~/Library/Application Support/Suprenam/` (MacOS)
- `~/.config/suprenam/` (Linux)
- `%HOMEPATH%\"AppData\Roaming\Suprenam\` (Windows)

There, it will put the logs (`"log.txt"` + some backups) and a configuration file (`"config.json"`) in which you can specify the text editor to use. For instance, VS-Code is the default when the command `code` is installed in your PATH; if you prefer Sublime Text, just replace the corresponding line by:

- macOS and Linux:
  ```json
    "editor_command": "subl -w",
  ```
- Windows
  ```json
    "editor_command": "subl.exe -w",
  ```

Many such commands are provided in [editor_commands.md](/src/editor_commands.md), and nothing prevents you from writing your own in the configuration file.

----

## How it works

- Suprenam starts by determining the items to rename. They can be provided:
  - directly, as a batch of **several files of folders**;
  - semi-directly, as a **single folder**: this folder will be renamed, along with all its children (both visible and hidden);
  - indirectly, as a **single text file** (mandatory suffix: `.txt`) containing the items to rename (one path by line). Note that a single non-text file will be treated as in the first case.
- Suprenam retrieves the [**inodes**](https://en.wikipedia.org/wiki/Inode) of the items to be renamed. These unique numeric identifiers will serve as an invariant throughout the renaming process.
- It creates a temporary TSV file associating each inode with its name. In case all items are siblings (i.e., have the same parent), the list is flat ; otherwise, a group is created for each parent.
- Note that the list is sorted in “natural order” (e.g., _foobar9_ before _foobar10_, and _[cote, coteau, crottez, crotté, côte, côté]_ as _[cote, côte, côté, coteau, crotté, crottez]_).
- Suprenam opens this file by invoking the editor command found in the [configuration file](#configuring-suprenam). If none is specified, it parses [`editor_commands.md`](/src/editor_commands.md) and defaults to the first one that happens to work on your system.
- Once the TSV file is opened, Suprenam waits for you to make the desired changes.
- When it is closed, its content is parsed.
  - Any deletion or change to non-inodes lines is ignored.
  - The deletion of one, several or even all of the inodes is tolerated.
  - However, any inode creation or duplication is considered as a typo, and makes the program to abort without renaming anything.
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
