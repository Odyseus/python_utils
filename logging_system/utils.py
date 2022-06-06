# -*- coding: utf-8 -*-
"""
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import MutableMapping
    from typing import Any

    from .._vendor.logging_system import FileHandlerFormatterOptions
    from .._vendor.logging_system import StreamHandlerFormatterOptions

import logging
import os

from ..ansi_colors import colorize
from ..ansi_colors import console_supports_color
from ..misc_utils import get_system_tempdir

from . import log_levels


class NoFileFilter(logging.Filter):
    """Filter file handler records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Is the specified record to be logged?

        Parameters
        ----------
        record : logging.LogRecord
            Record to filter.

        Returns
        -------
        bool
            If the specified record should be logged.
        """
        return getattr(record, "to_file", True)


class NoStreamFilter(logging.Filter):
    """Filter stream handler records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Is the specified record to be logged?

        Parameters
        ----------
        record : logging.LogRecord
            Record to filter.

        Returns
        -------
        bool
            If the specified record should be logged.
        """
        return getattr(record, "to_stream", True)


class OnceFilter(logging.Filter):
    """Filter to display a message only once.

    Attributes
    ----------
    messages : dict[str, list]
        Messages storage.
    """

    def __init__(self, name: str = "") -> None:
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        name : str, optional
            Filter name.
        """
        super().__init__(name)
        self.messages: dict[str, list] = {}

    def filter(self, record: logging.LogRecord) -> bool:
        """Is the specified record to be logged?

        Parameters
        ----------
        record : logging.LogRecord
            Record to filter.

        Returns
        -------
        bool
            If the specified record should be logged.
        """
        if getattr(record, "once", ""):
            params = self.messages.setdefault(record.msg, [])
            if record.args in params:
                return False

            params.append(record.args)

        return True


class CustomLoggerAdapter(logging.LoggerAdapter):
    """LoggerAdapter allowing ``message_only`` and ``once`` keywords.

    Attributes
    ----------
    KEYWORDS : list[str]
        Extra keyword arguments.

        - ``color`` (str | None): The name of a color from the :py:mod:`ansi_colors` module used \
        to colorize a message.
        - ``file_fmt`` (str | None): A format string used by the ``fmt`` parameter of a \
        :py:class:`FileHandlerFormatter` class.
        - ``message_only`` (bool): Log only the message and no other details like logger name, \
        logging level, etc.
        - ``no_color`` (bool): Do not attempt to colorize a message.
        - ``nonl`` (bool): No new line after a message.
        - ``once`` (bool): Log a message only once.
        - ``stream_fmt`` (str | None): A format string used by the ``fmt`` parameter of a \
        :py:class:`StreamHandlerFormatter` class.
        - ``to_file`` (bool): Log to file.
        - ``to_stream`` (bool): Log to stream.
    """

    KEYWORDS: list[str] = [
        "color",
        "file_fmt",
        "message_only",
        "no_color",
        "nonl",
        "once",
        "stream_fmt",
        "to_file",
        "to_stream",
    ]

    def log(  # type: ignore[override]
        self, level: str | int, msg: str, *args: Any, **kwargs: Any
    ) -> None:
        """Log message.

        Parameters
        ----------
        level : str | int
            Logging level name of numeric value.
        msg : str
            Message to log.
        *args : Any
            Arguments.
        **kwargs : Any
            Keyword arguments.
        """
        if isinstance(level, int):
            super().log(level, msg, *args, **kwargs)
        else:
            level = level.upper()
            levelno = log_levels.get(level, log_levels["INFO"])["numeric_value"]
            super().log(levelno, msg, *args, **kwargs)

    def process(
        self, msg: str, kwargs: MutableMapping[str, Any]
    ) -> tuple[str, MutableMapping[str, Any]]:
        """Process record.

        Grab all keyword arguments passed to a log function and insert them into the
        ``extra`` parameter.

        Parameters
        ----------
        msg : str
            Log message.
        kwargs : MutableMapping[str, Any]
            Keyword arguments.

        Returns
        -------
        tuple[str, MutableMapping[str, Any]]
            Passed parameters modified.
        """
        extra = kwargs.setdefault("extra", {})
        for keyword in self.KEYWORDS:
            if keyword in kwargs:
                extra[keyword] = kwargs.pop(keyword)

        return (msg, kwargs)

    def handle(self, record: logging.LogRecord) -> None:
        """Handle record.

        Parameters
        ----------
        record : logging.LogRecord
            Record to handle.
        """
        self.logger.handle(record)


class FileHandlerFormatter(logging.Formatter):
    """File handler formatter.

    Attributes
    ----------
    default_format_str : str
        Default format string.
    message_only_format_str : str
        Message only format string.
    """

    default_format_str: str = "%(asctime)s:%(levelname)s: %(message)s"
    message_only_format_str: str = "%(message)s"

    def __init__(self, options: FileHandlerFormatterOptions = {}) -> None:
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        options : FileHandlerFormatterOptions, optional
            Formatter options.
        """
        self._format_str: str = options.get("format_str", self.default_format_str)
        self._obfuscate_user_home: bool = options.get("obfuscate_user_home", True)
        self._user_home: str = os.path.expanduser("~")

    def format(self, record: logging.LogRecord) -> str:
        """Format log record.

        Parameters
        ----------
        record : logging.LogRecord
            The log record to format.

        Returns
        -------
        str
            The formatted message.
        """
        fmt: str = getattr(record, "file_fmt", None) or self._format_str

        if getattr(record, "message_only", False):
            fmt = self.message_only_format_str

        formatter: logging.Formatter = logging.Formatter(fmt)
        message: str = formatter.format(record)

        if self._obfuscate_user_home:
            message: str = message.replace(self._user_home, "~")

        return message


class StreamHandlerFormatter(logging.Formatter):
    """Stream handler formatter.

    Attributes
    ----------
    default_format_str : str
        Default format string.
    message_only_format_str : str
        Message only format string.
    """

    default_format_str: str = "%(name)s:%(levelname)s: %(message)s"
    message_only_format_str: str = "%(message)s"

    def __init__(self, options: StreamHandlerFormatterOptions = {}) -> None:
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        options : StreamHandlerFormatterOptions, optional
            Formatter options.
        """
        self._format_str: str = options.get("format_str", self.default_format_str)
        self._obfuscate_user_home: bool = options.get("obfuscate_user_home", True)
        self._user_home: str = os.path.expanduser("~")

    def format(self, record: logging.LogRecord) -> str:
        """Format log record.

        Parameters
        ----------
        record : logging.LogRecord
            The log record to format.

        Returns
        -------
        str
            The formatted message.
        """
        fmt: str = getattr(record, "stream_fmt", None) or self._format_str

        if getattr(record, "message_only", False):
            fmt = self.message_only_format_str

        formatter: logging.Formatter = logging.Formatter(fmt)
        message: str = formatter.format(record)

        if self._obfuscate_user_home:
            message: str = message.replace(self._user_home, "~")

        if not getattr(record, "no_color", False) and console_supports_color:
            color: str | None = getattr(record, "color", None)

            if color is not None:
                return colorize(message, color)
            elif record.levelname in log_levels:
                return colorize(message, log_levels[record.levelname]["color"])

        return message


class NewLineStreamHandler(logging.StreamHandler):
    """StreamHandler which switches line terminator by record.nonl flag."""

    def emit(self, record: logging.LogRecord) -> None:
        """Modify log message terminator before emiting log record.

        Parameters
        ----------
        record : logging.LogRecord
            Log record.
        """
        try:
            self.acquire()
            if getattr(record, "nonl", False):
                self.terminator = ""
            super().emit(record)
        finally:
            self.terminator = "\n"
            self.release()


def generate_rotating_log_path(
    storage_dir: str | bool = False,
    file_name: str | None = None,
) -> str:
    """Generate a log file path.

    If the base directory of the generated file path doesn't exists, it will be created.

    Parameters
    ----------
    storage_dir : str | bool, optional
        Storage directory for log files.
    file_name : str | None, optional
        Name for the log file.

    Returns
    -------
    str
        Full path to the log file.

    Raises
    ------
    dir_creation_error
        Error trying to create the logs storage directory. Either the current user lacks write
        permissions, or a file or symbolic link(?) exists at that location.
    RuntimeError
        A file name should be specified for the log file and the storage directory shouldn't be
        a falsy value.
    """
    if file_name is None:
        raise RuntimeError("A file name should be specified for the log file.")

    if not storage_dir:
        raise RuntimeError(
            "This function should not be called with a falsy value for its `storage_dir` parameter."
        )

    if storage_dir is True:
        storage_dir = os.path.join(get_system_tempdir(), file_name)

    if not os.path.isdir(storage_dir):
        try:
            os.makedirs(storage_dir)
        except OSError as dir_creation_error:
            raise dir_creation_error

    return os.path.abspath(os.path.join(storage_dir, f"{file_name}.log"))


if __name__ == "__main__":
    pass
