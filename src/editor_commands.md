# Text editors usable by Suprenam

## Caution

This file is used by [`get_editor_command.py`](/src/get_editor_command.py) to retrieve the first command that is installed on the current system. If you modify it and want a line to be parsed, follow the format:

```
- **Application name** (platforms): `command`
```

## Text editors and IDEs ordered by decreasing popularity

- **Visual Studio Code** (macOS, Linux): `code -w`
- **Visual Studio** (Windows)
- **IntelliJ**
- **Notepad++**
- **Vim** (macOS): `/Applications/MacVim.app/Contents/bin/mvim -f -g`
- **Android Studio**
- **Sublime Text** (macOS, Linux): `subl -w`
- **PyCharm** (macOS): `open -a PyCharm.app --wait`
- **PyCharm CE** (macOS): `open -a "PyCharm CE.app" --wait`
- **Eclipse**
- **Xcode**
- **Atom**
- **IPython/Jupyter**
- **Webstorm**
- **PHPStorm**
- **NetBeans**
- **Emacs**
- **Neovim**
- **Rider**
- **RStudio**
- **RubyMine**
- **TextMate** (macOS): `mate -w`

Source: _Integrated development environment_, [Stack Overflow Developer Survey, 2021](https://insights.stackoverflow.com/survey/2021).

## Niche text editors and fallbacks

- **TextEdit** (macOS): `open -neW` (open a new instance of TextEdit)

## Mock editor for testing

- **Mock editor** (mockOS): `mock_command`
