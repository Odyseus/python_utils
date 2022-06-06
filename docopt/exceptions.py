# -*- coding: utf-8 -*-
"""Exceptions.
"""
from __future__ import annotations


class DocoptLanguageError(Exception):
    """Error in construction of usage-message by developer."""


class DocoptExit(SystemExit):
    """Exit in case user invoked program with incorrect arguments.

    Attributes
    ----------
    usage : str
        Description
    """

    usage: str = ""

    def __init__(self, message: str = "") -> None:
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        message : str, optional
            Description
        """
        super().__init__((message + "\n" + self.usage).strip())
