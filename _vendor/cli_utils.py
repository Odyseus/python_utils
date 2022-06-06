# -*- coding: utf-8 -*-
"""Typing for cli_utils module.
"""
from __future__ import annotations


class CommandLineInterfaceSubClass:

    def __init__(self, docopt_args: dict) -> None:
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        docopt_args : dict
            The dictionary of arguments as returned by docopt parser.
        """
        ...

    def run(self) -> None:
        ...
