# -*- coding: utf-8 -*-
"""Repeating timer.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

import threading


class RepeatingTimer:
    """Repeating timer.

    Attributes
    ----------
    args : tuple
        Argumentsto pass to the executed function.
    func : Callable[..., Any]
        The function to be executed by the timer.
    interval_s : int | float
        Timer execution interval in seconds.
    is_running : bool
        Timer running flag.
    kwargs : dict
        Keyword argumentsto pass to the executed function.
    timer : threading.Timer | None
        The timer instance.
    """

    def __init__(self, interval_ms: int | float, func: Callable[..., Any], *args, **kwargs) -> None:
        """Initialization.

        Parameters
        ----------
        interval_ms : int | float
            Timer execution interval in milliseconds.
        func : Callable[..., Any]
            The function to be executed by the timer.
        *args
            Argumentsto pass to the executed function.
        **kwargs
            Keyword argumentsto pass to the executed function.
        """
        self.interval_s: int | float = interval_ms / 1000
        self.func: Callable[..., Any] = func
        self.args: tuple = args
        self.kwargs: dict = kwargs
        self.timer: threading.Timer | None = None
        self.is_running: bool = False

    def set_func(self, func: Callable[..., Any], *args, **kwargs) -> None:
        """Set timer function callback.

        Parameters
        ----------
        func : Callable[..., Any]
            The function to be executed by the timer.
        *args
            Argumentsto pass to the executed function.
        **kwargs
            Keyword argumentsto pass to the executed function.
        """
        self.func: Callable[..., Any] = func
        self.args: tuple = args
        self.kwargs: dict = kwargs

    def set_interval(self, interval_ms: int) -> None:
        """Set repeating interval.

        Parameters
        ----------
        interval_ms : int
            Timer execution interval in milliseconds.
        """
        self.interval_s: int = interval_ms / 1000

    def start(self) -> None:
        """Start timer."""
        self.timer = threading.Timer(self.interval_s, self._callback)
        self.timer.start()
        self.is_running = True

    def cancel(self) -> None:
        """Cancel timer."""
        assert isinstance(self.timer, threading.Timer)
        self.timer.cancel()
        self.is_running = False

    def _callback(self) -> None:
        """Method that the timer will call."""
        self.func(*self.args, **self.kwargs)
        self.start()
