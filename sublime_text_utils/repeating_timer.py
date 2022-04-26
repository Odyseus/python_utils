# -*- coding: utf-8 -*-
"""Repeating timer.
"""
import threading


class RepeatingTimer:
    """Repeating timer.

    Attributes
    ----------
    args
        Argumentsto pass to the executed function.
    func : function
        The function to be executed by the timer.
    interval_s : TYPE
        Description
    is_running : bool
        Description
    kwargs
        Keyword argumentsto pass to the executed function.
    timer : threading.Timer
        The timer instance.
    """
    def __init__(self, interval_ms, func, *args, **kwargs):
        """Initialization.

        Parameters
        ----------
        interval_ms : int
            Timer execution interval in milliseconds.
        func : function
            The function to be executed by the timer.
        *args
            Argumentsto pass to the executed function.
        **kwargs
            Keyword argumentsto pass to the executed function.
        """
        self.interval_s = interval_ms / 1000
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.timer = None
        self.is_running = False

    def set_func(self, func, *args, **kwargs):
        """Set timer function callback.

        Parameters
        ----------
        func : function
            The function to be executed by the timer.
        *args
            Argumentsto pass to the executed function.
        **kwargs
            Keyword argumentsto pass to the executed function.
        """
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def set_interval(self, interval_ms):
        """Set repeating interval.

        Parameters
        ----------
        interval_ms : int
            Timer execution interval in milliseconds.
        """
        self.interval_s = interval_ms / 1000

    def start(self):
        """Start timer.
        """
        self.timer = threading.Timer(self.interval_s, self._callback)
        self.timer.start()
        self.is_running = True

    def cancel(self):
        """Cancel timer.
        """
        assert isinstance(self.timer, threading.Timer)
        self.timer.cancel()
        self.is_running = False

    def _callback(self):
        """Method that the timer will call.
        """
        self.func(*self.args, **self.kwargs)
        self.start()
