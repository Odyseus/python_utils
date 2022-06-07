
## Python modules used in different projects

**The minimum supported Python version is 3.7.**

### Third party modules

- [bottle](https://github.com/bottlepy/bottle): A fast, simple and lightweight [WSGI](https://wsgi.readthedocs.io/en/latest/) micro web-framework for Python.
- [case_conversion](https://github.com/AlejandroFrias/case-conversion): A module to convert strings between pascal, camel, snake, screaming snake, dot, dash (hyphen), forward slash /, backslash \ cases, and separated words.
- [colour](https://github.com/vaab/colour): A module to convert and manipulate common color representations (HEX, RGB, HSL, etc.).
- [demjson3](https://pypi.org/project/demjson3/): A module for encoding, decoding, and syntax-checking JSON data.
- [diff_match_patch](https://github.com/google/diff-match-patch): A module that offers robust algorithms to perform the operations required for synchronizing plain text.
- [docopt](https://github.com/docopt/docopt): A pythonic command line arguments parser. This is a slightly modified version:
    - Print help "headers" in bold.
    - Re-declared some strings as raw strings (``r"..."``) to avoid some invalid escape sequence linter warnings.
- [html2text](https://github.com/Alir3z4/html2text): Convert HTML to Markdown-formatted text. Modifications:
    - Changed all defaults.
    - Changed `HTML2Text` class to be used as context manager.
    - Removed boolean CLI option `--dash-unordered-list` in favor of actually choosing the unordered list mark with the added `--ul-item-mark` CLI option.
    - Removed boolean CLI option `--asterisk-emphasis` in favor of actually choosing the strong and emphasis marks with the added `--strong-mark` and `--emphasis-mark` CLI options.
    - Removed initial indentation on rendered lists and changed indentation to 4 spaces.
    - Changed the `mark_code` option (`--mark-code` CLI option) to add triple back ticks instead of `[code][/code]` *tags*.
- **menu:** Slightly modified version of the [Menu](https://pypi.python.org/pypi/Menu) Python module to easily create CLI menus.
    - Changed some default values to suit my needs.
    - Some aesthetic changes for better readability of the menu items on the screen.
    - This modified version doesn't clear the screen every time a menu is opened.
- [lazy_import](https://github.com/jmrichardson/lazy_import): A module for lazy loading of Python modules.
- [mistune](https://github.com/lepture/mistune): A markdown parser in pure Python with renderer feature.
- **multi_select:** Slightly modified version of the [picker](https://github.com/MSchuwalow/picker) Python module.
- [parso](https://github.com/davidhalter/parso): A Python parser that supports error recovery and round-trip parsing for different Python versions.
- [polib](https://bitbucket.org/izi/polib): A library to manipulate, create and modify `gettext` files (pot, po and mo files).
- [Pyperclip](https://github.com/asweigart/pyperclip): A cross-platform Python module for copy and paste clipboard functions.
- [PyPNG](https://github.com/drj11/pypng): A pure Python library for PNG image encoding/decoding.
- [PyYAML](https://github.com/yaml/pyyaml): A YAML parser and emitter for Python.
- [sublime_lib](https://github.com/SublimeText/sublime_lib): A utility library for Sublime Text providing a variety of convenience features for other packages to use.
- [svgelements](https://github.com/meerk40t/svgelements): High fidelity SVG parsing and geometric rendering. The goal is to successfully and correctly process SVG for use with any scripts that may need or want to use SVG files as geometric data.
- [titlecase](https://github.com/ppannuto/python-titlecase): Module to change all words to Title Caps, and attempt to be clever about SMALL words like a/an/the in the input.
- [tqdm](https://pypi.python.org/pypi/tqdm): A fast and extensible progress bar for Python and CLI.
