# Text editors supported by Suprenam

## Caution

By default, [`get_editor_command.py`](/src/get_editor_command.py) uses this file to retrieve the first command that is installed on your operating system. Should you modify it or want an additional/modified line to be parsed, follow the format:

```
- **Application name** (platforms): `command`
```

Some of these commands are currently untested and/or unknown. Any help to fix them or fill in the blanks is welcome: submit a pull request with a new version of this file.

## Text editors and IDEs (ordered by decreasing popularity)

- **Visual Studio Code** (macOS, Linux, Windows): `code --wait`
- **Visual Studio** (Windows)
- **IntelliJ** (macOS, Linux, Windows): `idea --wait`
- **Notepad++** (Windows): `notepad++.exe -multiInst -nosession` (open a new instance)
- **Vim** (macOS): `/Applications/MacVim.app/Contents/bin/mvim -g --nofork` (run using GUI in the foreground)
- **Android Studio**
- **Sublime Text** (macOS, Linux): `subl --wait`
- **PyCharm** (macOS): `open -a PyCharm.app --wait`
- **PyCharm CE** (macOS): `open -a "PyCharm CE.app" --wait`
- **Eclipse**
- **Xcode**
- **Atom** (macOS, Linux, Windows): `atom --wait`
- **IPython/Jupyter**
- **Webstorm**
- **PHPStorm**
- **NetBeans**
- **Emacs**
- **Neovim** (macOS, Linux, Windows): `nvim`
- **Rider**
- **RStudio**
- **RubyMine**
- **TextMate** (macOS): `mate -w`

Source: _Integrated development environment_, [Stack Overflow Developer Survey, 2021](https://insights.stackoverflow.com/survey/2021).

## Fallbacks, pre-installed and niche text editors

### MacOS

- **TextEdit** (macOS): `open -e --new --wait-apps` (open a new instance)

### Windows

- **Notepad** (Windows): `notepad.exe`

### Linux Ubuntu

- **Gedit** (Linux): `gedit`
- **Kate** (Linux): `kate`
- **Leadpad** (Linux): `leadpad`
- **Mousepad** (Linux): `mousepad`
- **Pluma** (Linux): `pluma`
- **Nano** (Linux): `nano`
- **Vim** (Linux): `vim`
- **Vim** (Linux): `vi`

Source: _What are the default text editors in different flavours of Ubuntu?_ [Stack Overlow](https://askubuntu.com/a/913637).

## Mock editor for testing

- **Mock editor** (mockOS): `mock_command`
