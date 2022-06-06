# -*- coding: utf-8 -*-
"""CLI prompts and confirmation "dialogs" utilities.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

import sys
import termios
import tty

from . import exceptions
from .ansi_colors import colorize


def confirm(prompt: str | None = None, response: bool = False) -> bool:
    """Prompts for yes or no response from the user.

    Parameters
    ----------
    prompt : str | None, optional
        The prompt text.
    response : bool, optional
        "response" should be set to the default value assumed by the caller when
        user simply press ENTER.

    Returns
    -------
    bool
        True for "yes" or False for "no".

    Raises
    ------
    exceptions.KeyboardInterruption
        Halt execution on Ctrl + C press.

    Note
    ----
    Based on: `Prompt the user for confirmation (Python recipe) \
    <http://code.activestate.com/recipes/541096-prompt-the-user-for-confirmation>`__.

    **Modifications**:

    - Eradicated Python 2 code and added *transparent handling* of \
    upper/lower case input responses.

    Examples
    --------

    >>> confirm(prompt='Create Directory?', response=True)   # doctest: +SKIP
    Create Directory? [Y|n]:
    True
    >>> confirm(prompt='Create Directory?', response=False)  # doctest: +SKIP
    Create Directory? [N|y]:
    False
    >>> confirm(prompt='Create Directory?', response=False)  # doctest: +SKIP
    Create Directory? [N|y]: y
    True
    """

    if prompt is None:
        prompt = "Confirm"

    if response:
        prompt = "**%s [%s/%s]:** " % (prompt, "Y", "n")
    else:
        prompt = "**%s [%s/%s]:** " % (prompt, "N", "y")

    try:
        while True:
            # Lower the input case just so I don't have to micro-manage the answer.
            ans: str = input(colorize(prompt)).lower()

            if not ans:
                return response

            if ans not in ["y", "n"]:
                print(colorize("**Please enter y or n.**", "warning"))
                continue

            if ans == "y":
                return True

            if ans == "n":
                return False
    except KeyboardInterrupt:
        raise exceptions.KeyboardInterruption()


def term_input(prompt: str) -> str:
    """Get input from terminal.

    Parameters
    ----------
    prompt : str
        Text to be prompted with.

    Returns
    -------
    str
        Entered string.

    Note
    ----
    Based on: Utilities found in `Sphinx <https://github.com/sphinx-doc/sphinx>`__

    **Modifications**:

    - Eradicated Python 2 specific code.
    """
    print(prompt, end="")
    return input("")


def nonempty(x: str) -> str:
    """Check for non empty.

    Parameters
    ----------
    x : str
        String to check.

    Returns
    -------
    str
        The string passed.

    Raises
    ------
    exceptions.ValidationError
        Raise if empty.

    Note
    ----
    Based on: Utilities found in `Sphinx <https://github.com/sphinx-doc/sphinx>`__

    **Modifications**:

    - Eradicated Python 2 specific code.
    """
    if not x:
        raise exceptions.ValidationError("Please enter some text.")

    return x


def term_decode(text: str) -> str:
    """Decode terminal input.

    Parameters
    ----------
    text : str
        Entered text.

    Returns
    -------
    str
        Decoded text.

    Note
    ----
    Based on: Utilities found in `Sphinx <https://github.com/sphinx-doc/sphinx>`__

    **Modifications**:

    - Eradicated Python 2 specific code.
    """
    if isinstance(text, str):
        return text

    print(
        colorize(
            "* Note: non-ASCII characters entered "
            "and terminal encoding unknown -- assuming "
            "UTF-8 or Latin-1.",
            "warning",
        )
    )

    try:
        text = text.decode("utf-8")
    except UnicodeDecodeError:
        text = text.decode("latin1")

    return text


def do_prompt(
    d: dict,
    key: str,
    text: str,
    default: str | None = None,
    validator: Callable[[str], str] = nonempty,
):
    """Prompt function for interactively ask user for data.

    Parameters
    ----------
    d : dict
        A dictionary of options.
    key : str
        The "key" to change from "d".
    text : str
        The prompt text.
    default : str | None, optional
        Default option if none entered.
    validator : Callable[[str], str], optional
        A function to validate the input if needed.

    Raises
    ------
    exceptions.KeyboardInterruption
        Halt execution on Ctrl + C press.

    Note
    ----
    Based on: Utilities found in `Sphinx <https://github.com/sphinx-doc/sphinx>`__

    **Modifications**:

    - Eradicated Python 2 specific code.
    """
    try:
        prompt: str = ""

        while True:
            if default is not None:
                prompt = "**> %s:\n> Default [**%s**]:** " % (text, default)
            else:
                prompt = "**> %s:** " % text

            prompt = colorize(prompt)
            x: str = term_input(prompt).strip()

            if default and not x:
                x = default

            x = term_decode(x)

            try:
                x = validator(x)
            except exceptions.ValidationError as err:
                print(colorize("*** %s**" % str(err), "warning"))
                continue
            break
    except (KeyboardInterrupt, SystemExit):
        raise exceptions.KeyboardInterruption()
    else:
        d[key] = x


def read_char(txt: str) -> str:
    """Read character.

    Read single characters from standard input.

    Parameters
    ----------
    txt : str
        Message to display.

    Returns
    -------
    str
        The read character.
    """
    print(colorize(txt))
    fd: int = sys.stdin.fileno()
    old_settings: list = termios.tcgetattr(fd)

    try:
        tty.setraw(sys.stdin.fileno())
        ch: str = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

    return ch


if __name__ == "__main__":
    pass
