# -*- coding: utf-8 -*-
"""Command line interface utilities.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ._vendor.cli_utils import CommandLineInterfaceSubClass

import os
import sys

from . import exceptions
from . import logging_system
from .docopt import docopt

if sys.version_info < (3, 5):
    raise exceptions.WrongPythonVersion()


class CommandLineInterfaceSuper:
    """Command line interface super class.

    It handles the arguments parsed by the docopt module.

    Attributes
    ----------
    logger : logging_system.Logger | None
        The logger.
    """

    _cli_header_blacklist: list[bool] = []
    _print_log_blacklist: list[bool] = []
    _inhibit_logger_list: list[bool] = []

    def __init__(self, app_name: str, logs_storage_dir: str = "UserData/logs") -> None:
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        app_name : str
            Application name.
        logs_storage_dir : str, optional
            Log files storage location.
        """
        self._app_name: str = app_name
        self.logger: logging_system.Logger | None = None

        if not self._inhibit_logger_list or not any(self._inhibit_logger_list):
            self.logger = logging_system.Logger(
                logger_name=app_name,
                stream_handler_formatter_options={"format_str": "%(message)s"},
                use_file_handler=logs_storage_dir,
            )

        self._display_cli_header()

    def _display_cli_header(self) -> None:
        """Display CLI header.
        """
        if self.logger and (not self._cli_header_blacklist or not any(self._cli_header_blacklist)):
            self.logger.header(self._app_name)
            print("")

    def print_log_file(self) -> None:
        """Print the path to the log file used by the current logger.
        """
        if self.logger and (not self._print_log_blacklist or not any(self._print_log_blacklist)):
            print()
            self.logger.sub_section()
            self.logger.warning("**Log file location:**", to_file=False)
            self.logger.warning("**%s**" % self.logger.get_log_file(), to_file=False)
            self.logger.sub_section()

    def run(self) -> None:
        """Execute the assigned action stored in self.action if any.

        Raises
        ------
        exceptions.MethodNotImplemented
            See :any:`exceptions.MethodNotImplemented`
        """
        raise exceptions.MethodNotImplemented("run")

    def _system_executable_generation(self, **kwargs) -> None:
        """See :any:`template_utils.system_executable_generation`

        Parameters
        ----------
        **kwargs
            See :any:`template_utils.system_executable_generation`
        """
        from . import template_utils

        template_utils.system_executable_generation(**kwargs)

    def _display_manual_page(self, man_page_path: str) -> None:
        """Display manual page.

        Parameters
        ----------
        man_page_path : str
            The absolute path to the manual page.
        """
        from subprocess import run

        run(["man", man_page_path])


def run_cli(
    flag_file: str = "",
    docopt_doc: str = "",
    app_name: str = "",
    app_version: str = "",
    app_status: str = "",
    cli_class: type[CommandLineInterfaceSubClass] | None = None,
):
    """Initialize main command line interface.

    Parameters
    ----------
    flag_file : str, optional
        The name of a "flag" file.
    docopt_doc : str, optional
        docopt docstring.
    app_name : str, optional
        Application name.
    app_version : str, optional
        Application version.
    app_status : str, optional
        Application status.
    cli_class : type[CommandLineInterfaceSubClass] | None, optional
        An sub-class of ``cli_utils.CommandLineInterfaceSuper``.

    Raises
    ------
    exceptions.BadExecutionLocation
        Do not allow to run any command if the *flag* file isn't found where it should be.
        See :any:`exceptions.BadExecutionLocation`.
    """
    if not os.path.exists(flag_file):
        raise exceptions.BadExecutionLocation()

    if cli_class is not None:
        arguments: dict = docopt(
            docopt_doc,
            version="%s %s%s" % (app_name, app_version, " (%s)" % app_status if app_status else ""),
        )
        cli: CommandLineInterfaceSubClass = cli_class(arguments)
        cli.run()


if __name__ == "__main__":
    pass
