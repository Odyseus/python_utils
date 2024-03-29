# -*- coding: utf-8 -*-
"""Shell utilities.
"""
from shutil import get_terminal_size


def get_cli_header(name: str, char: str = "#") -> str:
    """Get a "decorated header".

    Get a "decorated header" to display at the beginning of the CLI execution (or whenever it is
    needed).

    Parameters
    ----------
    name : str
        The application name or a "title" to display as a "header".
    char : str, optional
        The "decorator" character.

    Returns
    -------
    str
        The actual "header".
    """
    term_length: int = get_terminal_size((80, 24))[0] or 80
    sep: str = get_cli_separator(char)
    sub_sep: str = "%s" % (int((term_length - (len(name) + 2)) / 2) * char)
    mid: str = "%s %s %s" % (sub_sep, name, sub_sep)

    while True:
        if len(mid) < term_length:
            mid += char
            continue

        if len(mid) >= term_length:
            break

    header: str = sep + "\n"
    header += mid[:term_length] + "\n"
    header += sep

    return header


def get_cli_separator(char: str = "#") -> str:
    """Get a "decorated separator".

    Get a "decorated separator" to display whenever it is needed.

    Parameters
    ----------
    char : str, optional
        The "decorator" character.

    Returns
    -------
    str
        The actual "separator".
    """
    term_length: int = get_terminal_size((80, 24))[0] or 80
    return "%s" % (term_length * char)


if __name__ == "__main__":
    pass
