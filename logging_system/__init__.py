# -*- coding: utf-8 -*-
"""A very simple logging system.

Note
----
I have to name this module ``logging_system`` and not just ``logging`` due to the retarded fact
that type checkers will not recognize the stadard library's module whe using ``import logging``.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._vendor.logging_system import LogLevelsData


log_levels: dict[str, LogLevelsData] = {
    "CRITICAL": {"color": "critical", "numeric_value": 50},
    "FATAL": {"color": "critical", "numeric_value": 50},
    "ERROR": {"color": "error", "numeric_value": 40},
    "WARNING": {"color": "warning", "numeric_value": 30},
    "WARN": {"color": "warning", "numeric_value": 30},
    "INFO": {"color": "default", "numeric_value": 20},
    "DEBUG": {"color": "default", "numeric_value": 10},
    "NOTSET": {"color": "default", "numeric_value": 0},
}


from .logger import Logger  # noqa: F401


if __name__ == "__main__":
    pass
