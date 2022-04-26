# -*- coding: utf-8 -*-
"""Events manager.
"""
import traceback

from collections import defaultdict


class Events:
    """docstring for Events

    Attributes
    ----------
    listeners : collections.defaultdict
        Functions storage.
    map_fn_to_topic : dict
        Functions to topics map.
    """

    def __init__(self):
        """Initialization.
        """
        self.listeners = defaultdict(set)
        self.map_fn_to_topic = {}

    def destroy(self):
        """Perform cleanup of all stored events.
        """
        self.listeners.clear()
        self.map_fn_to_topic.clear()
        self.listeners = defaultdict(set)
        self.map_fn_to_topic = {}

    def subscribe(self, topic, fn):
        """Register event.

        Parameters
        ----------
        topic : str
            Event name.
        fn : method
            Method to register.
        """
        self.listeners[topic].add(fn)

    def unsubscribe(self, topic, fn):
        """Unregister event.

        Parameters
        ----------
        topic : str
            Event name.
        fn : method
            Method to unregister.
        """
        try:
            self.listeners[topic].remove(fn)
        except KeyError:
            pass

    def broadcast(self, topic, payload={}):
        """Emit event.

        Parameters
        ----------
        topic : srt
            Event name.
        payload : dict, optional
            Parameters passed to executed method.
        """
        for fn in self.listeners.get(topic, []):
            try:
                fn(**payload)
            except Exception:
                traceback.print_exc()

    def on(self, topic):
        """Event registration decorator.

        Parameters
        ----------
        topic : str
            Event name.

        Returns
        -------
        method
            Decorator function.
        """

        def inner(fn):
            """Decorator.

            Parameters
            ----------
            fn : method
                Method to execute.

            Returns
            -------
            method
                Method to execute.
            """
            self.subscribe(topic, fn)
            self.map_fn_to_topic[fn] = topic
            return fn

        return inner

    def off(self, fn):
        """Remove event.

        Parameters
        ----------
        fn : method
            Method to unregister.
        """
        topic = self.map_fn_to_topic.get(fn, None)
        if topic:
            self.unsubscribe(topic, fn)


if __name__ == "__main__":
    pass
