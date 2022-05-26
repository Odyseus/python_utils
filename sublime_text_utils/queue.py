# -*- coding: utf-8 -*-
"""Queue management utilities.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

import threading


class Queue:
    """Queue manager.

    Attributes
    ----------
    timers : dict[str, threading.Timer]
        Timers storage.
    """

    def __init__(self) -> None:
        """See :py:meth:`object.__init__`."""
        self.timers: dict[str, threading.Timer] = {}

    def debounce(self, callback: Callable[..., Any], delay: int, key: str) -> threading.Timer:
        """Execute a method after a delay.

        Parameters
        ----------
        callback : Callable[..., Any]
            Method to execute.
        delay : int
            Execution delay.
        key : str
            Timer registration key.

        Returns
        -------
        threading.Timer
            Instantiated timer.
        """
        try:
            self.timers[key].cancel()
        except KeyError:
            pass

        self.timers[key] = timer = threading.Timer(delay / 1000, callback)
        timer.start()
        return timer

    def cleanup(self, key: str) -> None:
        """Unregister a timer.

        Parameters
        ----------
        key : str
            Timer registration key.
        """
        try:
            self.timers.pop(key).cancel()
        except KeyError:
            pass

    def unload(self) -> None:
        """Unregister all timers.

        Returns
        -------
        None
            Stop looping(?).
        """
        while True:
            try:
                _key, timer = self.timers.popitem()
            except KeyError:
                return
            else:
                timer.cancel()


if __name__ == "__main__":
    pass
