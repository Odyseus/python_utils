# -*- coding: utf-8 -*-
"""Typing for logging_system module.
"""
from __future__ import annotations

from typing import TypedDict


class StreamHandlerFormatterOptions(TypedDict, total=False):
    """:py:class:`logging_system.StreamHandlerFormatter` ``options`` parameter.

    Attributes
    ----------
    format_str : str
        The format string used by the ``fmt`` parameter of a :py:class:`logging.Formatter` class.
        The detfault format is ``"%(name)s:%(levelname)s: %(message)s"``.
    obfuscate_user_home : bool
        If all instances of the user's home path found in a log message should be replaced by
        the ``~`` character.
    """

    format_str: str
    obfuscate_user_home: bool


class FileHandlerFormatterOptions(TypedDict, total=False):
    """:py:class:`logging_system.FileHandlerFormatter` ``options`` parameter.

    Attributes
    ----------
    format_str : str
        The format string used by the ``fmt`` parameter of a :py:class:`logging.Formatter` class.
        The detfault format is ``"%(asctime)s:%(levelname)s: %(message)s"``.
    obfuscate_user_home : bool
        If all instances of the user's home path found in a log message should be replaced by
        the ``~`` character.
    """

    format_str: str
    obfuscate_user_home: bool


class FileHandlerOptions(TypedDict, total=False):
    """:py:class:`logging_system.Logger` ``file_handler_options`` parameter.

    See :py:class:`logging.handlers.RotatingFileHandler` for more details.

    Attributes
    ----------
    backupCount : int
        Amount of log files to keep when rotating. Default is ``10``.
    delay : bool
        If the file opening should be deferred until the first call to
        :py:meth:`logging.handlers.RotatingFileHandler.emit`. Default is ``False``.
    encoding : str
        Encoding to open the file with. Default ``None``.
    maxBytes : int
        Size in bytes at which log files should be rotated. Default is ``1048576`` (1MB).
    mode : str
        File opening mode. Default is ``a`` (append).
    """

    backupCount: int
    delay: bool
    encoding: str
    maxBytes: int
    mode: str


class LogLevelsData(TypedDict):
    """:py:attr:`logging_system._log_levels` data.

    Attributes
    ----------
    color : str
        The color of the logged message.
    numeric_value : int
        The numeric value of a logging level.
    """

    color: str
    numeric_value: int
