# Text editors supported by Suprenam

## Caution

By default, [`get_editor_command.py`](/src/get_editor_command.py) uses this file to retrieve the first command that is installed on your operating system. Should you modify it or want an additional/modified line to be parsed, follow the format:

```
| Application name | platforms | `command` |
```

Most of the following commands come from the [Pro Git Book](https://git-scm.com/about) (Scott Chacon and Ben Straub). Some are currently untested and/or unknown. Any help to fix them or fill in the blanks is welcome: submit a pull request with an updated version of this file.

## Text editors and IDEs (ordered by decreasing popularity)

| Editor | Platform | Command |
|:-------|:---------|:--------|
| Visual Studio Code | macOS, Linux, Windows | `code --wait` |
| Visual Studio | Windows | |
| IntelliJ | macOS, Linux, Windows | `idea --wait` |
| Notepad++ | Windows | `'C:\Program Files\Notepad\notepad.exe' -multiInst -notabbar -nosession -noPlugin` |
| Vim | macOS | `/Applications/MacVim.app/Contents/bin/mvim -g --nofork` |
| Vim | Linux |  `vim --nofork` |
| Gvim | Windows | `'C:\Program Files\Vim\vim72\gvim.exe' --nofork '%*'` |
| Android Studio | | |
| Sublime Text | macOS, Linux | `subl --new-window --wait` |
| Sublime Text | Windows | `'C:\Program Files\Sublime Text 3\sublime_text.exe' -w` |
| PyCharm | macOS | `open -a PyCharm.app --wait` |
| PyCharm CE | macOS | `open -a "PyCharm CE.app" --wait` |
| Eclipse | | |
| Xcode | | |
| Atom | macOS, Linux, Windows | `atom --wait` |
| IPython/Jupyter | | |
| Webstorm | | |
| PHPStorm | | |
| NetBeans | | |
| Emacs | macOS, Linux | `emacs` |
| Neovim | macOS, Linux, Windows | `nvim` |
| Rider | | |
| RStudio | | |
| RubyMine | | |
| TextMate | macOS | `mate -w` |

## Niche text editors (by alphabetic order)

| Editor | Platform | Command |
|:-------|:---------|:--------|
| BBEdit | macOS | `bbedit --wait` |
| Gedit | Linux | `gedit --wait --new-window` |
| Kate | Linux | `kate` |
| Leadpad | Linux | `leadpad` |
| Mousepad | Linux | `mousepad` |
| Nova | macOS | `nova --wait` |
| Pluma | Linux | `pluma` |
| Scratch | Linux | `scratch-text-editor` |
| Textpad | Windows | `'C:\Program Files\TextPad 5\TextPad.exe' -m` |
| TextWrangler | macOS | `edit --wait` |
| UltraEdit | Windows | `Uedit32` |
| VSCodium | macOS, Linux, Windows |  `codium --wait` |
| WordPad | Windows | `'C:\Program Files\Windows NT\Accessories\wordpad.exe'` |
| Xi | macOS, Linux, Windows |  `xi --wait` |

## Pre-installed fallbacks (one per platform)

| Editor | Platform | Command |
|:-------|:---------|:--------|
| TextEdit | macOS | `open -e --new --wait-apps` |
| Nano | Linux | `nano -w` |
| Notepad | Windows | `notepad.exe` |
| Mock editor | mockOS (for testing purpose) | `mock_default_command` |

# Sources

- _Git commands setup and config_, [Core editor](https://git-scm.com/book/en/v2/Appendix-C%3A-Git-Commands-Setup-and-Config#ch_core_editor).
- _Integrated development environment_, [Stack Overflow Developer Survey, 2021](https://insights.stackoverflow.com/survey/2021).
- _What are the default text editors in different flavours of Ubuntu?_ [Stack Overlow](https://askubuntu.com/a/913637).
