# -*- coding: utf-8 -*-
"""
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from .._vendor.logging_system import FileHandlerFormatterOptions
    from .._vendor.logging_system import FileHandlerOptions
    from .._vendor.logging_system import StreamHandlerFormatterOptions

import logging
import os
import sys

from logging.handlers import RotatingFileHandler

from ..shell_utils import get_cli_header
from ..shell_utils import get_cli_separator

from . import log_levels
from .utils import CustomLoggerAdapter
from .utils import FileHandlerFormatter
from .utils import NewLineStreamHandler
from .utils import NoFileFilter
from .utils import NoStreamFilter
from .utils import OnceFilter
from .utils import StreamHandlerFormatter
from .utils import generate_rotating_log_path


class Logger:
    """Logger class."""

    def __init__(
        self,
        logger_name: str | None = None,
        stream_handler_formatter_options: StreamHandlerFormatterOptions = {},
        file_handler_formatter_options: FileHandlerFormatterOptions = {},
        file_handler_options: FileHandlerOptions = {},
        use_file_handler: bool | str = False,
    ) -> None:
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        logger_name : str | None, optional
            A name for the logger. If not specified, the class name will be used.
        stream_handler_formatter_options : StreamHandlerFormatterOptions, optional
            Options to pass to :py:class:`StreamHandlerFormatter` formatter.
            See :py:class:`StreamHandlerFormatterOptions` for more details.
        file_handler_formatter_options : FileHandlerFormatterOptions, optional
            Options to pass to :py:class:`FileHandlerFormatter` formatter.
            See :py:class:`FileHandlerFormatterOptions` for more details.
        file_handler_options : FileHandlerOptions, optional
            Arguments to pass to :py:class:`logging.handlers.RotatingFileHandler` handler.
            See :py:class:`FileHandlerOptions` for more details.
        use_file_handler : bool | str, optional
            If logging to a log file should be allowed. It can be a boolean or a path to a folder
            where log files will be stored. If ``True``, the logs storage location will be a folder
            with the exact same name as the ``logger_name`` parameter created inside the
            system's temporary directory.
        """
        self._logger_name: str = logger_name or self.__class__.__name__
        self._log_file: str | None = None

        if use_file_handler:
            self._log_file = generate_rotating_log_path(
                storage_dir=use_file_handler,
                file_name=self._logger_name,
            )

        self._user_home: str = os.path.expanduser("~")
        _logger: logging.Logger = logging.getLogger(self._logger_name)

        # NOTE: Clear all handlers.
        for handler in _logger.handlers[:]:
            _logger.removeHandler(handler)

        self._file_handler: logging.handlers.RotatingFileHandler | None = None

        if self._log_file:
            self._file_handler = RotatingFileHandler(
                filename=self._log_file,
                mode=file_handler_options.get("mode", "a"),
                maxBytes=file_handler_options.get("maxBytes", 1048576),
                backupCount=file_handler_options.get("backupCount", 10),
                encoding=file_handler_options.get("encoding", None),
                delay=file_handler_options.get("delay", False),
            )
            self._file_handler.addFilter(NoFileFilter())
            self._file_handler.setFormatter(
                FileHandlerFormatter(options=file_handler_formatter_options)
            )
            _logger.addHandler(self._file_handler)

        self._stream_handler: logging.StreamHandler = NewLineStreamHandler()
        self._stream_handler.setFormatter(
            StreamHandlerFormatter(options=stream_handler_formatter_options)
        )
        self._stream_handler.addFilter(OnceFilter())
        self._stream_handler.addFilter(NoStreamFilter())
        _logger.addHandler(self._stream_handler)

        self._logger: logging.LoggerAdapter = CustomLoggerAdapter(_logger, {})

        self.set_logging_level()

    def _handle_logging_level(self, logging_level: str | int) -> int:
        """Handle logging level.

        Parameters
        ----------
        logging_level : str | int
            The logging level to handle.

        Returns
        -------
        int
            The numeric value of a logging level.
        """
        level: int = logging.INFO

        if isinstance(logging_level, int):
            level = logging_level
        elif isinstance(logging_level, str):
            logging_level = logging_level.upper()
            level = getattr(logging, logging_level, logging.INFO)

            if logging_level not in log_levels:
                self._logger.log(
                    logging.WARNING,
                    f"Attempting to set a non-existent logging level (**{logging_level}**).",
                )

        return level

    def set_logging_level(self, logging_level: str | int = "INFO") -> None:
        """Set logger and handlers logging level.

        Parameters
        ----------
        logging_level : str | int, optional
            The name of one of the logging levels defined in :py:attr:`logging_system.log_levels`.
        """
        level: int = self._handle_logging_level(logging_level)
        self.set_logger_level(level)
        self.set_stream_handler_level(level)
        self.set_file_handler_level(level)

        self._logger.log(logging.DEBUG, f"Current logging level: **{logging_level}**")

    def set_logger_level(self, logging_level: str | int) -> None:
        """Set logger logging level.

        Parameters
        ----------
        logging_level : str | int
            The numeric value of a logging level or the name of an existent logging level.
        """
        self._logger.setLevel(self._handle_logging_level(logging_level))

    def set_stream_handler_level(self, logging_level: str | int) -> None:
        """Set stream handler logging level.

        Parameters
        ----------
        logging_level : str | int
            The numeric value of a logging level or the name of an existent logging level.
        """
        self._stream_handler.setLevel(self._handle_logging_level(logging_level))

    def set_file_handler_level(self, logging_level: str | int) -> None:
        """Set file handler logging level.

        Parameters
        ----------
        logging_level : str | int
            The numeric value of a logging level or the name of an existent logging level.
        """
        if self._file_handler is not None:
            self._file_handler.setLevel(self._handle_logging_level(logging_level))

    def get_log_file(self) -> str:
        """Get log file path.

        Returns
        -------
        str
            The path to the log file.
        """
        return self._log_file

    def header(self, title: str) -> None:
        """Print a header.

        Parameters
        ----------
        title : str
            Header title.
        """
        self._logger.log(
            logging.INFO, get_cli_header(title, char="#"), message_only=True, no_color=True
        )

    def separator(self) -> None:
        """Print a separator.
        """
        self._logger.log(
            logging.INFO, get_cli_separator(char="#"), message_only=True, no_color=True
        )

    def section(self) -> None:
        """Print a section separator.
        """
        self._logger.log(
            logging.INFO, get_cli_separator(char="="), message_only=True, no_color=True
        )

    def sub_section(self) -> None:
        """Print a sub-section separator.
        """
        self._logger.log(
            logging.INFO, get_cli_separator(char="-"), message_only=True, no_color=True
        )

    def log_dry_run(self, msg: Any, **kwargs: Any) -> None:
        """Log an exception message.

        Parameters
        ----------
        msg : Any
            Message to log.
        **kwargs : Any
            Keyword arguments.
        """
        self._logger.log(logging.INFO, f"**[DRY_RUN]** {msg}", color="lightmagenta", **kwargs)

    def exception(self, msg: Any, **kwargs: Any) -> None:
        """Log an exception message.

        Parameters
        ----------
        msg : Any
            Message to log.
        **kwargs : Any
            Keyword arguments.
        """
        self._logger.log(logging.ERROR, msg, exc_info=sys.exc_info(), **kwargs)

    def critical(self, msg: Any, **kwargs: Any) -> None:
        """Critical message.

        Parameters
        ----------
        msg : Any
            Message to log.
        **kwargs : Any
            Keyword arguments.
        """
        self._logger.log(logging.CRITICAL, msg, **kwargs)

    def error(self, msg: Any, **kwargs: Any) -> None:
        """Error message.

        Parameters
        ----------
        msg : Any
            Message to log.
        **kwargs : Any
            Keyword arguments.
        """
        self._logger.log(logging.ERROR, msg, **kwargs)

    def warning(self, msg: Any, **kwargs: Any) -> None:
        """Warning message.

        Parameters
        ----------
        msg : Any
            Message to log.
        **kwargs : Any
            Keyword arguments.
        """
        self._logger.log(logging.WARNING, msg, **kwargs)

    def success(self, msg: Any, **kwargs: Any) -> None:
        """Success message.

        Parameters
        ----------
        msg : Any
            Message to log.
        **kwargs : Any
            Keyword arguments.
        """
        self._logger.log(logging.INFO, msg, color="success", **kwargs)

    def info(self, msg: Any, **kwargs: Any) -> None:
        """Info message.

        Parameters
        ----------
        msg : Any
            Message to log.
        **kwargs : Any
            Keyword arguments.
        """
        self._logger.log(logging.INFO, msg, **kwargs)

    def debug(self, msg: Any, **kwargs: Any) -> None:
        """Debug message.

        Parameters
        ----------
        msg : Any
            Message to log.
        **kwargs : Any
            Keyword arguments.
        """
        self._logger.log(logging.DEBUG, msg, **kwargs)


if __name__ == "__main__":
    pass
