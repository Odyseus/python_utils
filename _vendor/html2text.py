# -*- coding: utf-8 -*-
"""Typing for html2text module.
"""
from __future__ import annotations

from typing import TypedDict


class OutCallback:
    """Possible custom replacement method for :py:meth:`HTML2Text.outtextf` (which appends lines of text)."""

    def __call__(self, s: str) -> None:
        """See :py:meth:`object.__call__`.

        Parameters
        ----------
        s : str
            String to append to output storage list.
        """
        ...


class ValidOptionsData(TypedDict):
    """Valid options data."""

    typ: type
    doc: str
    default: str | bool | int
