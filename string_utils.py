# -*- coding: utf-8 -*-
"""Common utilities to perform string manipulation operations.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import logging_system
    from collections.abc import Callable
    from collections.abc import Generator
    from typing import Any

import fnmatch
import os
import re
import unicodedata

from collections import UserDict
from collections.abc import Mapping
from collections.abc import Sequence

from . import file_utils


class __DictClone(UserDict):
    """__DictClone

    Handle missing keys in a dictionary used by str.format_map(). It will just clear
    non-defined variables out of the formatted string.
    """

    def __missing__(self, key: str) -> str:
        """See :py:meth:`object.__missing__`.

        Parameters
        ----------
        key : str
            The missing key.

        Returns
        -------
        str
            A blank string.
        """
        return ""


def split_on_uppercase(string: str, keep_contiguous: bool = True) -> list:
    """Split string on uppercase.

    Parameters
    ----------
    string : str
        The string to split by its uppercase characters.
    keep_contiguous : bool, optional
        Option to indicate we want to keep contiguous uppercase characters together.

    Returns
    -------
    list
        The parts of the passed string.

    Note
    ----
    Based on: `Split a string at uppercase letters <https://stackoverflow.com/a/40382663>`__.

    Example
    -------

    >>> from python_utils.string_utils import split_on_uppercase
    >>> split_on_uppercase("HelloWorld")
    ['Hello', 'World']
    """

    string_length: int = len(string)
    is_lower_around: Callable[[int], bool] = (
        lambda i: string[i - 1].islower() or string_length > (i + 1) and string[i + 1].islower()
    )

    start: int = 0
    parts: list = []

    for i in range(1, string_length):
        if string[i].isupper() and (not keep_contiguous or is_lower_around(i)):
            parts.append(string[start:i])
            start = i

    parts.append(string[start:])

    return parts


def do_replacements(data: str, replacement_data: list[tuple[Any, Any]]) -> str:
    """Do replacements.

    Parameters
    ----------
    data : str
        Data to modify.
    replacement_data : list[tuple[Any, Any]]
        List of tuples containing (template, replacement) data.

    Returns
    -------
    str
        Modified data.
    """
    for template, replacement in replacement_data:
        if template in data:
            data = data.replace(str(template), str(replacement))

    return data


def do_string_substitutions(
    dir_path: str,
    replacement_data: list[tuple[Any, Any]],
    allowed_extensions: str | tuple[str, ...] = (".py", ".bash", ".js", ".json", ".xml"),
    handle_file_names: bool = True,
    logger: logging_system.Logger | None = None,
) -> None:
    """Do substitutions.

    Parameters
    ----------
    dir_path : str
        Path to a directory where to perform string substitutions on.
    replacement_data : list[tuple[Any, Any]]
        Data used to perform string substitutions.
    allowed_extensions : str | tuple[str, ...], optional
        A tuple of file extensions that are allowed to be modified.
    handle_file_names : bool, optional
        Perform string substitutions on file names.
    logger : logging_system.Logger | None, optional
        The logger.
    """
    logger.info("**Performing string substitutions...**")

    for root, dirs, files in os.walk(dir_path, topdown=False):
        for fname in files:
            # Only deal with a limited set of file extensions.
            if not fname.endswith(allowed_extensions):
                continue

            file_path: str = os.path.join(root, fname)

            if os.path.islink(file_path):
                continue

            with open(file_path, "r+", encoding="UTF-8") as file:
                file_data = file.read()
                file.seek(0)
                new_file_data: str = do_replacements(file_data, replacement_data)

                if new_file_data != file_data:
                    file.write(new_file_data)
                    file.truncate()

            # Check and set execution permissions for Bash and Python scripts.
            # FIXME: Should I hard-code the file names that should be set as executable?
            # I don't see a problem setting all Python files as exec., since I only use
            # Python scripts, not Python modules.
            # Lets put a pin on it and revisit in the future.
            if fname.endswith((".py", ".bash")):
                if not file_utils.is_exec(file_path):
                    os.chmod(file_path, 0o755)

            if handle_file_names:
                fname_renamed: str = do_replacements(fname, replacement_data)

                if fname != fname_renamed:
                    os.rename(
                        file_path,
                        os.path.join(os.path.dirname(file_path), fname_renamed),
                    )

        for dname in dirs:
            dir_path: str = os.path.join(root, dname)

            if os.path.islink(dir_path):
                continue

            if handle_file_names:
                dname_renamed: str = do_replacements(dname, replacement_data)

                if dname != dname_renamed:
                    os.rename(dir_path, os.path.join(os.path.dirname(dir_path), dname_renamed))


def super_filter(
    names: list[str],
    inclusion_patterns: list[str] = [],
    exclusion_patterns: list[str] = [],
) -> list[str]:
    """Super filter.

    Enhanced version of fnmatch.filter() that accepts multiple inclusion and exclusion patterns.

    - If only ``inclusion_patterns`` is specified, only the names which match one or more \
    patterns are returned.
    - If only ``exclusion_patterns`` is specified, only the names which do not match any \
    pattern are returned.
    - If both are specified, the exclusion patterns take precedence.
    - If neither is specified, the input is returned as-is.

    Parameters
    ----------
    names : list[str]
        A list of strings to filter.
    inclusion_patterns : list[str], optional
        A list of patterns to keep in names.
    exclusion_patterns : list[str], optional
        A list of patterns to exclude from names.

    Returns
    -------
    list[str]
        A filtered list of strings.

    Note
    ----
    Based on: `Filtering with multiple inclusion and exclusion patterns \
    <https://codereview.stackexchange.com/a/74849>`__
    """
    included = multi_filter(names, inclusion_patterns) if inclusion_patterns else names
    excluded = multi_filter(names, exclusion_patterns) if exclusion_patterns else []
    return list(set(included) - set(excluded))


def multi_filter(names: list[str], patterns: list[str]) -> Generator[str, None, None]:
    """Multi filter.

    Generator function which yields the names that match one or more of the patterns.

    Parameters
    ----------
    names : list[str]
        A list of strings to filter.
    patterns : list[str]
        A list of patterns to match in names.

    Yields
    ------
    Generator[str, None, None]
        A name in names parameter that matches any of the patterns in patterns parameter.
    """
    for name in names:
        if any(fnmatch.fnmatch(name, pattern) for pattern in patterns):
            yield name


def get_valid_filename(string: str, separator: str = "_") -> str:
    """Get valid file name.

    Return the given string converted to a string that can be used for a clean
    filename.

    - Removes leading and trailing spaces.
    - Converts any succesion of white spaces into a single underscore (configurable, \
    althogh it cannot be anything other than a dash, an underscore or a dot).
    - Removes anything that is not an alphanumeric, dash, underscore, or dot.

    Parameters
    ----------
    string : str
        The string to validate.
    separator : str, optional
        Which character to use to replace white spaces.

    Returns
    -------
    str
        A *safe to use* string for file names.

    Note
    ----
    Based on: Utilities found in `Django Web framework <https://github.com/django/django>`__

    Example
    -------

    >>> from python_utils import string_utils
    >>> string_utils.get_valid_filename("john's portrait in 2004.jpg")
    'johns_portrait_in_2004.jpg'
    """
    string = re.sub(r"\s+", separator, str(string).strip())
    return re.sub(r"(?u)[^-\w.]", "", string)


def slugify(string: str, allow_unicode: bool = False) -> str:
    """Slugify.

    - Convert to ASCII if ``allow_unicode`` is False.
    - Convert spaces to hyphens.
    - Remove characters that aren't alphanumerics, underscores, or hyphens.
    - Convert to lowercase.
    - Strip leading and trailing whitespace.

    Parameters
    ----------
    string : str
        The string to slugify.
    allow_unicode : bool, optional
        Whether or not to allow unicode characters in the slugified string.

    Returns
    -------
    str
        A slugified string.

    Note
    ----
    Based on: Utilities found in `Django Web framework <https://github.com/django/django>`__

    Example
    -------

    >>> from python_utils import string_utils
    >>> string_utils.slugify("john's portrait in 2004.jpg")
    'johns-portrait-in-2004jpg'
    """
    string = str(string)

    if allow_unicode:
        string = unicodedata.normalize("NFKC", string)
    else:
        string = unicodedata.normalize("NFKD", string).encode("ascii", "ignore").decode("ascii")

    string = re.sub(r"[^\w\s-]", "", string).strip().lower()

    return re.sub(r"[-\s]+", "-", string)


def substitute_variables(variables: dict, value: Any) -> Any:
    """Substitute variables.

    This is a crude attempt to replicate the functionality of the function with the same name
    that uses a function called ``expand_variables`` provided by Sublime Text's API. It uses
    ``str.format_map()`` to replace variables found in a string.

    Parameters
    ----------
    variables : dict
        A dictionary containing variables as keys mapped to values to replace those variables.
    value : Any
        The str/list/dict containing the data where to perform substitutions.


    Returns
    -------
    Any
        The modified data.

    Note
    ----
    Borrowed from SublimeLinter.
    """
    if isinstance(value, str):
        # Workaround https://github.com/SublimeTextIssues/Core/issues/1878
        # (E.g. UNC paths on Windows start with double backslashes.)
        value = value.replace(r"\\", r"\\\\")

        if os.pardir + os.sep in value:
            value = os.path.normpath(value)

        value = os.path.expandvars(os.path.expanduser(value))

        return value.format_map(__DictClone(variables))
    elif isinstance(value, Mapping):
        return {key: substitute_variables(variables, val) for key, val in value.items()}
    elif isinstance(value, Sequence):
        return [substitute_variables(variables, item) for item in value]
    else:
        return value


if __name__ == "__main__":
    pass
