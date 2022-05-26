# -*- coding: utf-8 -*-
"""Reference to a bound method that permits the associated object to be garbage collected.

Based on `WeakMethod (Python recipe) <https://code.activestate.com/recipes/81253>`__.
"""
from __future__ import annotations

from weakref import ref


class _weak_callable:
    """Summary
    """

    def __init__(self, obj, func):
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        obj : TYPE
            Description
        func : TYPE
            Description
        """
        self._obj = obj
        self._meth = func

    def __call__(self, *args, **kws):
        """See :py:meth:`object.__call__`.

        Parameters
        ----------
        *args
            Description
        **kws
            Description

        Returns
        -------
        TYPE
            Description
        """
        if self._obj is not None:
            return self._meth(self._obj, *args, **kws)
        else:
            return self._meth(*args, **kws)

    def __getattr__(self, attr):
        """See :py:meth:`object.__getattr__`.

        Parameters
        ----------
        attr : TYPE
            Description

        Returns
        -------
        TYPE
            Description

        Raises
        ------
        AttributeError
            Description
        """
        if attr == "__self__":
            return self._obj
        elif attr == "__func__":
            return self._meth
        raise AttributeError(attr)


class WeakMethod:
    """Wraps a function or, more importantly, a bound method, in
    a way that allows a bound method's object to be GC'd, while
    providing the same interface as a normal weak reference.
    """

    def __init__(self, fn):
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        fn : TYPE
            Description

        Raises
        ------
        TypeError
            Description
        """
        if not callable(fn):
            raise TypeError("Argument must be callable")
        try:
            self._obj = ref(fn.__self__)
            self._meth = ref(fn.__func__)
        except AttributeError:
            # It's not a bound method.
            self._obj = None
            self._meth = ref(fn)

    def __call__(self):
        """See :py:meth:`object.__call__`.

        Returns
        -------
        TYPE
            Description
        """
        meth = self._meth()
        if meth is None:
            return None
        elif self._obj is None:
            return _weak_callable(None, meth)
        else:
            obj = self._obj()
            if obj is None:
                return None
            else:
                return _weak_callable(obj, meth)

    def __eq__(self, other):
        """See :py:meth:`object.__eq__`.

        Parameters
        ----------
        other : TYPE
            Description

        Returns
        -------
        TYPE
            Description
        """
        return (
            type(self) is type(other)
            and self._obj is other._obj
            and self._meth == other._meth
        )

    def __hash__(self):
        """See :py:meth:`object.__hash__`.

        Returns
        -------
        TYPE
            Description
        """
        return hash((id(self._obj), self._meth))


class WeakMethodProxy(WeakMethod):
    """Summary
    """

    def __call__(self, *args, **kwargs):
        """See :py:meth:`object.__call__`.

        Parameters
        ----------
        *args
            Description
        **kwargs
            Description

        Returns
        -------
        TYPE
            Description

        Raises
        ------
        ReferenceError
            Description
        """
        func = super().__call__()
        if func is None:
            raise ReferenceError("weak reference is gone")
        else:
            return func(*args, **kwargs)
