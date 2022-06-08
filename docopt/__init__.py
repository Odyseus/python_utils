# -*- coding: utf-8 -*-
"""Pythonic command-line interface parser that will make you smile.

- http://docopt.org.
- Repository and issue-tracker: https://github.com/docopt/docopt.
- Licensed under terms of MIT license (see LICENSE-MIT).
- Copyright (c) 2013 Vladimir Keleshev, vladimir@keleshev.com.

.. note::

    This is a slightly modified version of the docopt module.

    **Modifications**:

    - Print help "headers" in bold. It basically highlights in bold any line that doesn't start \
    with a white space character.
    - Re-declared some strings as raw strings (``r"..."``) to avoid some invalid escape \
    sequence linter warnings.
    - Added a basic Markdown parsing for highlighting the help message with bold text. \
    It will highlight in bold any text surrounded with double asterisks (e.g. **bold text**). \
    The parsing is done line by line. It should only be used to highlight words inside \
    options/commands descriptions.
    - Changed sections detection logic. The original module, and all of its forks, force the \
    indentation and the styling of the sections content. So, I K.I.S.S.'ed it because I simply \
    don't want to be forced to use the styling of a non-existing standard. Sections are now \
    defined with tags-like markup. The **Usage** section is marked up with the ``<usage></usage>`` \
    *tags* and the **Options** sections are marked up with the ``<options></options>`` *tags*.

.. important::

    Forget the existence of all current ``docopt`` forks!!!

    - `docopt-ng <https://github.com/jazzband/docopt-ng>`__: \
    It fixes nothing that is broken on the original docopt.
    - `docpie <https://github.com/TylerTemp/docpie>`__: \
    It fixes some of what is broken on the original docopt. But I can't tolerate the forcing down \
    the options section's throat the f*cking indent. The rest of added features are just \
    unnecessary bloat.

.. warning::

    Some warnings/workarounds to bypass some known issues with docopt.

    - Do not ever start a line with a hyphen (minus sign) inside ``docopt_doc``, except when \
    specifying options. ``docopt`` parses all lines starting with a hyphen as options without exceptions.
    - When an option is specified more than once inside the **Usage** section of ``docopt_doc``, \
    it might generate duplicated items.

    .. code:: python

        # Workaround `docopt issue <https://github.com/docopt/docopt/issues/134>`__:
        # Not perfect, but good enough for some of my particular usage cases.
        deduplicated_options = list(set(args["--option"]))

.. warning::

    Case for which I couldn't find a fix/workaround:

    .. code-block::

        Usage:
            app.py [-v | --verbose]...

        Options:

        -v, --verbose
            Verbose.

    If I call ``app.py -vvv`` the ``--verbose`` option should be exactly **3**, but **5** is given.

    **Addendum**

    I did find a workaround/fix for this. Instead of using the repeating *ellipsis* like this
    ``[-v | --verbose]...``, I can use them like this ``[-v... | --verbose...]``. The thing is,
    I switched to defining the repeating *ellipsis* *at group level* instead of individually for
    each option/argument because the arguments parsing performance plummeted when defined
    individually.

.. tip::

    Fixed arguments order.

    .. code:: python

        order_reference = [
            "First",
            "Second",
            "Third",
            "Fourth"
        ]
        # Sort the arguments so one doesn't have to worry about the order in which they are passed.
        # Source: https://stackoverflow.com/a/12814719.
        unordered_arguments = args["<arguments>"]
        # ["Fourth", "First", "Third", "Second"]
        unordered_arguments.sort(key=lambda x: order_reference.index(x))
        # ["First", "Second", "Third", "Fourth"]

        # Notes:
        # - unordered_arguments can have missing items.
        # - unordered_arguments cannot have items that aren't present in order_reference.

"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .elements import Pattern
    from .elements import Required

import re
import sys

from ..ansi_colors import console_supports_color

from .elements import Option
from .elements import OptionsShortcut
from .elements import ParsedOptionsDict
from .exceptions import DocoptExit
from .exceptions import DocoptLanguageError
from .parsers import Tokens
from .parsers import parse_argv
from .parsers import parse_defaults
from .parsers import parse_pattern
from .parsers import parse_section

__all__ = ["docopt", "DocoptExit"]
__version__ = "0.6.2"

_bold_markdown_re = re.compile(r"\*\*([^\*\*]*)\*\*")
_bold_markdown_placeholder = r"\033[1m\1\033[0m"
_section_tags = (
    "<usage>",
    "</usage>",
    "<options>",
    "</options>",
)


def formal_usage(section: str) -> str:
    """Summary

    Parameters
    ----------
    section : str
        Description

    Returns
    -------
    str
        Description
    """
    pu: list[str] = section.split()
    return "( " + " ".join(") | (" if s == pu[0] else s for s in pu[1:]) + " )"


def print_bold(s: str) -> None:
    """Summary

    Parameters
    ----------
    s : str
        Description
    """
    if console_supports_color:
        print(f"\033[1m{s}\033[0m")
    else:
        print(s)


def extras(help: bool, version: str, options: list, doc: str) -> None:
    """Summary

    Parameters
    ----------
    help : bool
        Description
    version : str
        Description
    options : list
        Description
    doc : str
        Description
    """
    if help and any((o.name in ("-h", "--help")) and o.value for o in options):
        for line in doc.strip("\n").splitlines():
            if line in _section_tags:
                continue

            if line.startswith("-"):
                print_bold(line)
            else:
                line = (
                    _bold_markdown_re.sub(_bold_markdown_placeholder, line)
                    if console_supports_color
                    else _bold_markdown_re.sub(r"\1", line)
                )
                print(line)
        sys.exit()

    if version and any(o.name == "--version" and o.value for o in options):
        print(version)
        sys.exit()


def docopt(
    doc: str,
    argv: list[str] | None = None,
    help: bool = True,
    version: str | None = None,
    options_first: bool = False,
) -> ParsedOptionsDict:
    """Parse ``argv`` based on command-line interface described in ``doc``.

    ``docopt`` creates your CLI based on the docstring that you pass as the ``doc``
    parameter. Such docstring can contain ``--options``, ``<positional-argument>``,
    ``commands``, which could be ``[optional]``, ``(required)``, ``(mutually | exclusive)``
    or ``repeated...``.

    Parameters
    ----------
    doc : str
        Description of your command-line interface.
    argv : list[str] | None, optional
        Argument vector to be parsed. sys.argv[1:] is used if not
        provided.
    help : bool, optional
        Set to False to disable automatic help on -h or --help
        options.
    version : str | None, optional
        If passed, the object will be printed if --version is in
        `argv`.
    options_first : bool, optional
        Set to True to require options precede positional arguments,
        i.e. to forbid options and positional arguments intermix.

    Returns
    -------
    ParsedOptionsDict
        A dictionary, where keys are names of command-line elements such as e.g.
        "--verbose" and "<path>", and values are the parsed values of those elements.

    Raises
    ------
    DocoptExit
        Description
    DocoptLanguageError
        Description

    Example
    -------
    >>> from python_utils.docopt import docopt
    >>> doc = '''
    ... Usage
    ... <usage>
    ...     my_program tcp <host> <port> [--timeout=<seconds>]
    ...     my_program serial <port> [--baud=<n>] [--timeout=<seconds>]
    ...     my_program (-h | --help | --version)
    ... </usage>
    ...
    ... Options
    ...
    ... <options>
    ... -h, --help
    ...     Show this screen and exit.
    ...
    ... --baud=<n>
    ...     Baudrate [default: 9600]
    ... </options>
    ...
    ... '''
    >>> argv = ['tcp', '127.0.0.1', '80', '--timeout', '30']
    >>> docopt(doc, argv)
    {'--baud': '9600',
     '--help': False,
     '--timeout': '30',
     '--version': False,
     '<host>': '127.0.0.1',
     '<port>': '80',
     'serial': False,
     'tcp': True}

    """
    argv = sys.argv[1:] if argv is None else argv
    usage_sections: list[str] = parse_section("usage", doc)

    if len(usage_sections) == 0:
        raise DocoptLanguageError("'Usage:' (case-insensitive) section not found.")

    if len(usage_sections) > 1:
        raise DocoptLanguageError("More than one 'Usage:' (case-insensitive) section.")

    DocoptExit.usage = "Usage:" + usage_sections[0]

    options: list[Option] = parse_defaults(doc)
    pattern: Required = parse_pattern(formal_usage(usage_sections[0]), options)
    parsed_argv: list[Pattern] = parse_argv(Tokens(argv), list(options), options_first)

    for options_shortcut in pattern.flat(OptionsShortcut):
        pattern_options: set[Option] = set(pattern.flat(Option))
        doc_options: set[Option] = set(parse_defaults(doc))
        options_shortcut.children = list(doc_options - pattern_options)

    extras(help, version, parsed_argv, doc)
    matched, left, collected = pattern.fix().match(parsed_argv)

    if matched and left == []:
        return ParsedOptionsDict([(a.name, a.value) for a in (pattern.flat() + collected)])

    if left:
        raise DocoptExit(f"Warning: found unmatched (duplicate?) arguments {left}.")

    raise DocoptExit()
