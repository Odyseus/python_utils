# -*- coding: utf-8 -*-
"""Events manager.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from typing import Any

import traceback

from collections import defaultdict


class Events:
    """docstring for Events

    Attributes
    ----------
    listeners : defaultdict
        Functions storage.
    map_fn_to_topic : dict
        Functions to topics map.
    """

    def __init__(self) -> None:
        """See :py:meth:`object.__init__`."""
        self.listeners: defaultdict = defaultdict(set)
        self.map_fn_to_topic: dict = {}

    def destroy(self) -> None:
        """Perform cleanup of all stored events."""
        self.listeners.clear()
        self.map_fn_to_topic.clear()
        self.listeners = defaultdict(set)
        self.map_fn_to_topic = {}

    def subscribe(self, topic: str, fn: Callable[..., Any]) -> None:
        """Register event.

        Parameters
        ----------
        topic : str
            Event name.
        fn : Callable[..., Any]
            Method to register.
        """
        self.listeners[topic].add(fn)

    def unsubscribe(self, topic: str, fn: Callable[..., Any]) -> None:
        """Unregister event.

        Parameters
        ----------
        topic : str
            Event name.
        fn : Callable[..., Any]
            Method to unregister.
        """
        try:
            self.listeners[topic].remove(fn)
        except KeyError:
            pass

    def broadcast(self, topic: str, payload: dict = {}) -> None:
        """Emit event.

        Parameters
        ----------
        topic : str
            Event name.
        payload : dict, optional
            Parameters passed to executed method.
        """
        for fn in self.listeners.get(topic, []):
            try:
                fn(**payload)
            except Exception:
                traceback.print_exc()

    def on(self, topic: str) -> Callable[[Callable[..., Any]], Any]:
        """Event registration decorator.

        Parameters
        ----------
        topic : str
            Event name.

        Returns
        -------
        Callable[[Callable[..., Any]], Any]
            Decorator function.
        """

        def inner(fn: Callable[..., Any]) -> Callable[..., Any]:
            """Decorator.

            Parameters
            ----------
            fn : Callable[..., Any]
                Method to execute.

            Returns
            -------
            Callable[..., Any]
                Method to execute.
            """
            self.subscribe(topic, fn)
            self.map_fn_to_topic[fn] = topic
            return fn

        return inner

    def off(self, fn: Callable[..., Any]) -> None:
        """Remove event.

        Parameters
        ----------
        fn : Callable[..., Any]
            Method to unregister.
        """
        topic: str | None = self.map_fn_to_topic.get(fn, None)
        if topic:
            self.unsubscribe(topic, fn)


if __name__ == "__main__":
    pass
