# -*- coding: utf-8 -*-
"""Miscellaneous utility functions.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .logging_system import Logger
    from datetime import timedelta
    from typing import Any

from datetime import datetime


def get_system_tempdir() -> str:
    """Get system's temporary directory.

    Returns
    -------
    str
        Path to system's temporary directory.
    """
    import tempfile

    return tempfile.gettempdir()


def get_date_time(type: str = "date") -> str:
    """Get date time.

    Parameters
    ----------
    type : str, optional
        The time "type" to return (Default: date).

    Returns
    -------
    str
        The current time formatted by the "type" passed.
    """
    if type == "appid":
        return datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
    elif type == "filename":
        return datetime.now().strftime("%Y-%m-%d_%H.%M.%S.%f")
    elif type == "function_name":
        return datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")
    else:  # type == "date"
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")


def micro_to_milli(date: str) -> str:
    """Microseconds to milliseconds.

    Convert a date string from using microseconds to use milliseconds.

    Parameters
    ----------
    date : str
        The date string to convert.

    Returns
    -------
    str
        The date string converted.
    """
    return date[:-6] + str("{0:03d}".format(int(int(date[-6:]) / 1000)))


def get_time_diff(s: str, e: str) -> str:
    """Get time difference.

    Parameters
    ----------
    s : str
        Start date.
    e : str
        End date.

    Returns
    -------
    str
        The difference in hours, minutes, seconds, and milliseconds between two dates.
    """
    start: datetime = datetime.strptime(s, "%Y-%m-%d %H:%M:%S.%f")
    ends: datetime = datetime.strptime(e, "%Y-%m-%d %H:%M:%S.%f")

    diff: timedelta = ends - start

    m, s = divmod(diff.seconds, 60)
    h, m = divmod(m, 60)
    ms: float = diff.microseconds / 1000

    return "%d hr/s, %d min/s, %d sec/s, %d msec/s" % (h, m, s, ms)


def merge_dict(
    first: Any,
    second: Any,
    logger: Logger = None,
    extend_lists: bool = True,
    append_to_lists: bool = True,
) -> Any:
    """Merges **second** dictionary into **first** dictionary and return merged result.

    It *deep merges* keys of type :any:`dict` and :any:`list`.
    Any other type is overwritten.

    Parameters
    ----------
    first : Any
        A dictionary to which to merge a second dictinary.
    second : Any
        A dictionary to merge into another dictionary.
    logger : Logger, optional
        The logger.
    extend_lists : bool, optional
        When dealing with lists, extend the ``first`` list one with the ``second`` one.
    append_to_lists : bool, optional
        If ``first`` is a list and ``second`` isn't, append ``second`` to ``first``.

    Returns
    -------
    Any
        A merged dictionary.
    """
    key: str = None
    try:
        if isinstance(first, list):
            # Lists can be only appended.
            if isinstance(second, list) and extend_lists:
                # Merge lists.
                first.extend(second)
            elif append_to_lists:
                # Append to list.
                first.append(second)
            else:
                # Overwrite list.
                first = second
        elif isinstance(first, dict):
            # Dictionaries must be merged.
            if isinstance(second, dict):
                for key in second:
                    if key in first:
                        first[key] = merge_dict(
                            first[key],
                            second[key],
                            extend_lists=extend_lists,
                            append_to_lists=append_to_lists,
                            logger=logger,
                        )
                    else:
                        first[key] = second[key]
            else:
                logger.warning('**Cannot merge non-dict "%s" into dict "%s"**' % (second, first))
        else:
            first = second
    except TypeError as err:
        logger.error(
            '**TypeError "%s" in key "%s" when merging "%s" into "%s"**' % (err, key, second, first)
        )

    return first


if __name__ == "__main__":
    pass
