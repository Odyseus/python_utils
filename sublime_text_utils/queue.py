# -*- coding: utf-8 -*-
"""Queue management utilities.
"""
import threading


class Queue:
    """Queue manager.

    Attributes
    ----------
    timers : dict
        Timers storage.
    """
    def __init__(self):
        """Initialization.
        """
        self.timers = {}

    def debounce(self, callback, delay, key):
        """Execute a method after a delay.

        Parameters
        ----------
        callback : method
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

    def cleanup(self, key):
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

    def unload(self):
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
