#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check and sort import statements on Python files.

Based on : `fiximports <https://github.com/gsemet/fiximports>`__.

.. note::

    **Differences with the original**

    - Removed the mechanism that decided if the data needed to be fixed. In the original script, the \
    data wasn't fixed if at least one *error* that cannot be handled was found \
    (multiple import statements on one line or parenthesis character found). In this fork, the data \
    will always be fixed no matter what.
    - Added capability to fix indented ``import`` statements. This has the advantage of fixing \
    import statements inside conditions, try/catch blocks etc., but also has the *disadvantage* of fixing imports inside docstrings. I can live with that for now.
    - Redesigned CLI interface.

        + Exposed for configuration all available options of the :py:meth:`FixImports.sort_import_groups` method.
        + Added support for reading from STDIN. The fixed output will be written into STDOUT.

Examples
--------

>>> from python_utils.fix_imports import FixImports
>>> from textwrap import dedent

Sorting and grouping.

>>> import_string = dedent(
...     '''
...     from abc import bbbb
...     from abc import aaaa
...     from abc import cccc
...     import datetime
...     import collections
...     '''
... )
>>> print(FixImports().sort_import_groups(data=import_string)[1])
<BLANKLINE>
import collections
import datetime
<BLANKLINE>
from abc import aaaa
from abc import bbbb
from abc import cccc
<BLANKLINE>

Sorting indented imports.

>>> import_string = dedent(
...     '''
...     MYPY = False
...     if MYPY:
...         from typing import Union
...         from types import TracebackType
...         from typing import Tuple
...         from types import MethodType
...         from typing import Any
...     '''
... )
>>> print(FixImports().sort_import_groups(data=import_string)[1])
<BLANKLINE>
MYPY = False
if MYPY:
    from types import MethodType
    from types import TracebackType
    from typing import Any
    from typing import Tuple
    from typing import Union
<BLANKLINE>

Split ``import`` statements.

>>> import_string = dedent(
...     '''
...     MYPY = False
...     if MYPY:
...         from typing import Union, MethodType, Any
...         from types import TracebackType, MethodType
...     '''
... )
>>> print(FixImports().sort_import_groups(data=import_string)[1])
<BLANKLINE>
MYPY = False
if MYPY:
    from types import MethodType
    from types import TracebackType
    from typing import Any
    from typing import MethodType
    from typing import Union
<BLANKLINE>

Ignore parenthesized grouped ``import`` statements but fix the rest of statements if needed.

>>> import_string = dedent(
...     '''
...     from abc import bbbb, aaaa, cccc
...     MYPY = False
...     if MYPY:
...         from types import (
...             MethodType,
...             TracebackType,
...         )
...         from typing import (
...             Any,
...             MethodType,
...             Union,
...         )
...     '''
... )
>>> print(FixImports().sort_import_groups(data=import_string)[1])
<BLANKLINE>
from abc import aaaa
from abc import bbbb
from abc import cccc
MYPY = False
if MYPY:
    from types import (
        MethodType,
        TracebackType,
    )
    from typing import (
        Any,
        MethodType,
        Union,
    )
<BLANKLINE>
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Iterator

import re
import sys

__version__ = (2022, 5, 12)

_import_re: re.Pattern = re.compile(r"^(^|\s+)import\s+(.*)")
_from_import_re: re.Pattern = re.compile(r"^(^|\s+)from\s+([a-zA-Z0-9\._]+)\s+import\s+(.*)$")


class FixImports:

    """Check and sort import statements of Python files.

    Attributes
    ----------
    group_start : int | None
        Mark the start of a group of ``import`` statements.
    groups : list[tuple[int, int]]
        Groups of import statements.
    """

    def __init__(self) -> None:
        """See :py:meth:`object.__init__`."""
        self.groups: list[tuple[int, int]] = []
        self.group_start: int | None = None

    def is_import_line(self, line: str) -> re.Match:
        """Check if the given line is an ``import`` statement.

        Parameters
        ----------
        line : str
            Content of a line.

        Returns
        -------
        re.Match
            Matches in content of line.
        """
        return _import_re.match(line) or _from_import_re.match(line)

    def is_bad_line_fixable(self, line: str) -> bool:
        """Check if the given line is fixable.

        Parameters
        ----------
        line : str
            Content of a line.

        Returns
        -------
        bool
            If the given line is an import line that can be handled.
        """
        if self.is_import_line(line) and "(" not in line and ";" not in line:
            return True
        return False

    def import_order(self, line: str) -> tuple[bool, bool, str]:
        """Define how import lines should be sorted.

        Parameters
        ----------
        line : str
            Content of a line.

        Returns
        -------
        tuple[bool, bool, str]
            A tuple of order criteria sorted by importance.
        """
        return (
            "__future__" not in line,  # Always put __future__ import first.
            _from_import_re.match(line) is not None,  # import before from import.
            line,  # Then lexicographic order.
        )

    def sort_import_groups(
        self,
        filename: str | None = None,
        data: str | None = None,
        split_import_statements: bool = True,
        sort_import_statements: bool = True,
    ) -> tuple[bool, str]:
        """Perform the analysis of the given data, print the errors found and try to split and
        sort the import statements.

        Parameters
        ----------
        filename : str | None, optional
            Used only for logging purposes.
        data : str | None, optional
            Data to analize.
        split_import_statements : bool, optional
            Split comma separated imports into their own lines.
        sort_import_statements : bool, optional
            Sort import statements.

        Returns
        -------
        tuple[bool, str]
            A tuple whose first element is a boolean representing if the data was modified and
            its second element the data iteself, modified or not.
        """
        filename = filename or "Line number"
        # BEWERE: Original had ``data.split("\n")``. Keep an eye on this.
        lines: list[str] = data.splitlines()

        # First split the import we can split
        newlines: list[str] = []
        self.groups = []
        self.group_start = None
        # NOTE: Store leading and trailing white spaces for later add them back.
        leading_ws = data[: len(data) - len(data.lstrip())]
        trailing_ws = data[len(data.rstrip()):]

        def maybe_end_group():
            """Maybe end import group."""
            if self.group_start is not None:
                self.groups.append((self.group_start, len(newlines)))
                self.group_start = None

        iter: Iterator = lines.__iter__()
        while True:
            try:
                line: str = iter.__next__()
            except StopIteration:
                break
            if self.is_import_line(line):
                # join any continuation lines (\\)
                while line[-1] == "\\":
                    line = line[:-1] + iter.__next__()
                if self.group_start is None:
                    self.group_start = len(newlines)

                if self.is_bad_line_fixable(line):
                    match: re.Match = _from_import_re.match(line)
                    if match:
                        indent: re.Match = match.group(1)
                        module: re.Match = match.group(2)
                        imports = sorted([s.strip() for s in match.group(3).split(",")])
                        if split_import_statements:
                            for imp in imports:
                                newlines.append("%sfrom %s import %s" % (indent, module, imp))
                        else:
                            newlines.append(
                                "%sfrom %s import %s" % (indent, module, ", ".join(imports))
                            )
                        continue
            else:
                maybe_end_group()
            newlines.append(line)

        maybe_end_group()

        # sort each group
        if sort_import_statements:
            lines: list[str] = newlines
            for start, end in self.groups:
                lines[start:end] = sorted(lines[start:end], key=self.import_order)

        # reiterate line by line to split mixed groups
        prev_import_line_type: str = ""
        splitted_groups_lines: list[str] = []
        for line in lines:
            if not line.strip() or not self.is_import_line(line):
                splitted_groups_lines.append(line)
                prev_import_line_type = ""
            else:
                import_match: re.Match = _import_re.match(line)
                from_match: re.Match = _from_import_re.match(line)
                current_line_type: str | None = None
                if import_match is not None:
                    module = import_match
                    current_line_type = "import"
                elif from_match is not None:
                    module = from_match
                    current_line_type = "from"
                assert current_line_type
                if prev_import_line_type and current_line_type != prev_import_line_type:
                    splitted_groups_lines.append("")
                prev_import_line_type = current_line_type
                splitted_groups_lines.append(line)

        fixed_data: str = leading_ws + "\n".join(splitted_groups_lines).strip() + trailing_ws

        return (fixed_data != data, fixed_data)


def main() -> None:
    """Main method.

    Raises
    ------
    err
        Encoding error.

    Note
    ----
    - When USING ``STDIN`` to ``STDOUT``, always output either the fixed data or the \
    unmodified data.
    - When fixing files, do not attempt to modify the files unless \
    the original data has being modified.
    """
    import argparse

    p: argparse.ArgumentParser = argparse.ArgumentParser()
    p.add_argument(
        "--no-split-import-statements",
        dest="split_import_statements",
        action="store_false",
        default=True,
        help="Split comma separated imports into their own lines. "
        "Parenthesized grouped imports are ignored.",
    )
    p.add_argument(
        "--no-sort-import-statements",
        dest="sort_import_statements",
        action="store_false",
        default=True,
        help="Sort import statements.",
    )
    p.add_argument("--version", action="version", version=".".join(map(str, __version__)))
    p.add_argument(
        "--decode-errors",
        dest="decode_errors",
        default="strict",
        type=str,
        help="How to handle decoding errors. Possible values: 'strict', 'ignore', 'replace'. "
        "It defaults to 'strict'.",
    )
    p.add_argument("filename", nargs="?", default=None)
    p.add_argument("encoding", nargs="?", default="utf-8")

    args: dict = dict(vars(p.parse_args()))
    filename: str | None = args.get("filename")
    to_file: bool = bool(filename and filename != "-")
    data: bytes | str | None = None

    if to_file:
        with open(filename, "rb") as fp:
            data = fp.read()
    else:
        data = sys.stdin.buffer.read()

    try:
        data = data.decode(encoding=args.get("encoding"), errors=args.get("decode_errors"))
    except UnicodeDecodeError as err:
        print("Warning: Use the --decode-errors=ignore flag.")
        raise err

    modified, fixed_data = FixImports().sort_import_groups(
        filename=filename if to_file else None,
        data=data,
        split_import_statements=args.get("split_import_statements"),
        sort_import_statements=args.get("sort_import_statements"),
    )

    if not modified:
        if to_file:
            sys.exit(1)
        else:
            sys.stdout.write(fixed_data)
            sys.exit(0)

    if to_file:
        with open(filename, "w") as fp:  # type: ignore[assignment]
            fp.write(fixed_data)  # type: ignore[arg-type]

        print(f"Imports successfully fixed for file: {filename}")
    else:
        sys.stdout.write(fixed_data)

    sys.exit(0)


if __name__ == "__main__":
    main()
