# -*- coding: utf-8 -*-
"""Utility to colorize terminal output.

Attributes
----------
COLOR_TABLE_4_BIT : dict[str, dict[str, str]]
    4-bit ANSI colors table. This table has all 4-bit ANSI color names mapped to their
    foreground and background color codes.
COLOR_TABLE_8_BIT : dict[str, str]
    8-bit ANSI colors table. This table has only 10 web color names and 4 contextual names
    mapped to their color codes.
console_supports_color : bool
    If console supports color or color is purposely disabled.

Notes
-----
I was forced to implement the 8-bit control sequences (256 colors) because the 4-bit
control sequences (16 colors) are a mess. The problem is that setting text to bold will also
switch a color to its bright version. For example, when setting text to yellow and bold, the text
will be actually light yellow. And light yellow is impossible to see on light backgrounds and eye
piercing on dark backgrounds. And since there isn't any other color of the 4-bit control sequences
that I can or would want to use as contextual warning, I switched to contextual colors based on
the 8-bit control sequences (256 colors).

The ``COLOR_TABLE_8_BIT`` table has only named colors that match the Web colors standard and
also the X11 standard. No other 8-bit ANSI color code has a color name that exists in either of
the mentioned standards.

There isn't a 24-bit color table becuase, COME ON, there are more than 16 millions colors (LOL).
Calling the :py:meth:`colorize_24_bit` function using
`RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__  values is easy enough. And if I ever
need to colorize the output of a console using named
`RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__  colors, I can simply use the
:py:mod:`colour.color_maps` module where I have maps of
`X11 color names <https://en.wikipedia.org/wiki/X11_color_names>`__ and
`W3C colors <https://en.wikipedia.org/wiki/Web_colors>`__ mapped to their RGB values.
"""
from __future__ import annotations

import os
import re
import sys

COLOR_TABLE_4_BIT: dict[str, dict[str, str]] = {
    "default": {"fg": "39", "bg": "49"},
    "black": {"fg": "30", "bg": "40"},
    "red": {"fg": "31", "bg": "41"},
    "green": {"fg": "32", "bg": "42"},
    "yellow": {"fg": "33", "bg": "43"},
    "blue": {"fg": "34", "bg": "44"},
    "magenta": {"fg": "35", "bg": "45"},
    "cyan": {"fg": "36", "bg": "46"},
    "lightgray": {"fg": "37", "bg": "47"},
    "darkgray": {"fg": "90", "bg": "100"},
    "lightred": {"fg": "91", "bg": "101"},
    "lightgreen": {"fg": "92", "bg": "102"},
    "lightyellow": {"fg": "93", "bg": "103"},
    "lightblue": {"fg": "94", "bg": "104"},
    "lightmagenta": {"fg": "95", "bg": "105"},
    "lightcyan": {"fg": "96", "bg": "106"},
    "white": {"fg": "97", "bg": "107"},
}

COLOR_TABLE_8_BIT: dict[str, str] = {
    # Web colors.
    "aqua": "51",
    "blue": "21",
    "cyan": "51",
    "fuchsia": "201",
    "green": "46",
    "lime": "46",
    "magenta": "201",
    "red": "196",
    "white": "231",
    "yellow": "226",
    # Contextual colors.
    "critical": "196",
    "error": "202",
    "success": "112",
    "warning": "214",
}


# NOTE: DO NOT TOUCH THIS! It works good enough. Do not ever try to tweak it again. NEVER!!!
_bold_markdown_re: re.Pattern = re.compile(r"\*{2}([\s\S]+?)\*{2}")
_bold_placeholder_4: str = r"\033[0m\033[1;49;{code}m\1\033[0m\033[0;49;{code}m"
_bold_placeholder_8: str = r"\033[0m\033[1;38;5;{code}m\1\033[0m\033[0;38;5;{code}m"
_bold_placeholder_24: str = r"\033[0m\033[1;38;2;{r};{g};{b}m\1\033[0m\033[0;38;2;{r};{g};{b}m"
_alpha: re.Pattern = re.compile(r"[^a-z]")
_sequence: re.Pattern = re.compile(r"(\x1b|\033).*?m")


def check_console_supports_color() -> bool:
    """Check if console supports color.

    Returns
    -------
    bool
        If console supports color or color is purposely disabled.

    Note
    ----
    Extracted from Sphinx.
    """
    if "NO_COLOR" in os.environ:
        return False
    if "FORCE_COLOR" in os.environ:
        return True
    if not hasattr(sys.stdout, "isatty"):
        return False
    if not sys.stdout.isatty():
        return False
    if "COLORTERM" in os.environ:
        return True
    term = os.environ.get("TERM", "dumb").lower()
    if term in ("xterm", "linux") or "color" in term:
        return True
    return False


console_supports_color: bool = check_console_supports_color()


def strip_sequences(s: str) -> str:
    """Strip escape sequences from a string.

    Parameters
    ----------
    s : str
        The string to clean up.

    Returns
    -------
    str
        The cleaned up string.

    Note
    ----
    Extracted from Sphinx.
    """
    return _sequence.sub("", s)


def colorize(text: str, name: str = "default") -> str:
    """Colorize text by color name.

    Parameters
    ----------
    text : str
        Text to colorize.
    name : str, optional
        Name of a color in one of the color tables.

    Returns
    -------
    str
        Colorized text.
    """
    name = _alpha.sub("", name.lower())

    if name in COLOR_TABLE_4_BIT:
        return colorize_4_bit(text, COLOR_TABLE_4_BIT[name]["fg"])
    elif name in COLOR_TABLE_8_BIT:
        return colorize_8_bit(text, COLOR_TABLE_8_BIT[name])

    return text


def colorize_4_bit(text: str, code: str | int | float) -> str:
    """Colorize text using 4-bit control sequences.

    Parameters
    ----------
    text : str
        Text to colorize.
    code : str | int | float
        ANSI color code.

    Returns
    -------
    str
        Colorized string.
    """
    if console_supports_color:
        code = _to_str_code(code)
        return (
            f"\033[0;49;{code}m"
            + _bold_markdown_re.sub(_bold_placeholder_4.format(code=code), str(text))
            + "\033[0m"
        )
    else:
        return _bold_markdown_re.sub(r"\1", str(text))


def colorize_8_bit(text: str, code: str | int) -> str:
    """Colorize text using 8-bit control sequences.

    Parameters
    ----------
    text : str
        Text to colorize.
    code : str | int
        ANSI color code.

    Returns
    -------
    str
        Colorized string.
    """
    if console_supports_color:
        code = _to_str_code(code)
        return (
            f"\033[0;38;5;{code}m"
            + _bold_markdown_re.sub(_bold_placeholder_8.format(code=code), str(text))
            + "\033[0m"
        )
    else:
        return _bold_markdown_re.sub(r"\1", str(text))


def colorize_24_bit(text: str, r: str | int, g: str | int, b: str | int) -> str:
    """Colorize text using 24-bit control sequences.

    Parameters
    ----------
    text : str
        Text to colorize.
    r : str | int
        Red channel proportion (0 to 255) of an
        `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ color.
    g : str | int
        Green channel proportion (0 to 255) of an
        `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ color.
    b : str | int
        Blue channel proportion (0 to 255) of an
        `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ color.

    Returns
    -------
    str
        Colorized string.
    """
    if console_supports_color:
        r = _to_str_code(r)
        g = _to_str_code(g)
        b = _to_str_code(b)
        return (
            f"\033[0;38;2;{r};{g};{b}m"
            + _bold_markdown_re.sub(_bold_placeholder_24.format(r=r, g=g, b=b), str(text))
            + "\033[0m"
        )
    else:
        return _bold_markdown_re.sub(r"\1", str(text))


def _to_str_code(code: str | int | float) -> str:
    """Convert a control sequence color code to a string.

    Parameters
    ----------
    code : str | int | float
        Control sequence color code.

    Returns
    -------
    str
        Control sequence color code.
    """
    return str(int(round(float(code))))


if __name__ == "__main__":
    pass
