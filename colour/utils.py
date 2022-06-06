# -*- coding: utf-8 -*-
"""Various utilities.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._vendor.colour import InputColor3Tuple

import traceback

from .constants import ALPHA_NUMERIC


def sanitize_color_name(color: str) -> str:
    """Sanitize color name.

    Sanitize a color name to possibly get a valid color name from the colors databases. Color names
    are composed only of lower-cased alpha-numeric characters. ``color`` is stripped of all alpha-numeric
    characters and lower cased.

    >>> from python_utils.colour.future_colour import Color, Web, RGB

    >>> Color("Alice Blue").web == Web.alice_blue == getattr(Web, "a l i c e b l u e")
    True

    >>> Color("Grey 33").rgb == RGB.grey_33 == getattr(RGB, "g r e y 3 3") == \
        Color("Gray 33").rgb == RGB.gray_33 == getattr(RGB, "g r a y 3 3")
    True

    Parameters
    ----------
    color : str
        A string that might be interpreted as a color name.

    Returns
    -------
    str
        Sanitized color name.
    """
    return ALPHA_NUMERIC.sub("", color).lower()


def hue2rgb(v1: float, v2: float, vH: float) -> float:
    """Private helper function (Do not call directly).

    Parameters
    ----------
    v1 : float
        Description
    v2 : float
        Description
    vH : float
        Rotation around the chromatic circle (between 0..1).

    Returns
    -------
    float
        Description
    """

    while vH < 0:
        vH += 1
    while vH > 1:
        vH -= 1

    if 6 * vH < 1:
        return v1 + (v2 - v1) * 6 * vH
    if 2 * vH < 1:
        return v2
    if 3 * vH < 2:
        return v1 + (v2 - v1) * ((2.0 / 3) - vH) * 6

    return v1


def with_metaclass(mcls):
    """Summary

    Parameters
    ----------
    mcls : TYPE
        Description

    Returns
    -------
    TYPE
        Description
    """

    def decorator(cls):
        """Summary

        Returns
        -------
        TYPE
            Description
        """
        body = vars(cls).copy()
        # clean out class body
        body.pop("__dict__", None)
        body.pop("__weakref__", None)
        return mcls(cls.__name__, cls.__bases__, body)

    return decorator


def color_scale(
    begin_hsl: InputColor3Tuple,
    end_hsl: InputColor3Tuple,
    nb: int,
) -> list[tuple[float, float, float]]:
    """Returns a list of ``nb`` color `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__
    tuples between ``begin_hsl`` and ``end_hsl``.

    Parameters
    ----------
    begin_hsl : InputColor3Tuple
        Description
    end_hsl : InputColor3Tuple
        Description
    nb : int
        Description

    Returns
    -------
    list[tuple[float, float, float]]
        Description

    Raises
    ------
    ValueError
        Description

    Examples
    --------

    >>> from python_utils.colour.future_colour import color_scale, HSL, HexS

    >>> [HSL(hsl).convert(HexS) for hsl in color_scale((0, 1, 0.5),
    ...                                                (1, 1, 0.5), 3)]
    ['#f00', '#0f0', '#00f', '#f00']

    >>> [HSL(hsl).convert(HexS)
    ...  for hsl in color_scale((0, 0, 0),
    ...                         (0, 0, 1),
    ...                         15)]
    ['#000', '#111', '#222', ..., '#ccc', '#ddd', '#eee', '#fff']

    Of course, asking for negative values is not supported:

    >>> color_scale((0, 1, 0.5), (1, 1, 0.5), -2)
    Traceback (most recent call last):
    ...
    ValueError: Unsupported negative number of colors (nb=-2).

    """

    if nb < 0:
        raise ValueError("Unsupported negative number of colors (nb=%r)." % nb)

    step: tuple[float, float, float] = (
        tuple([float(end_hsl[i] - begin_hsl[i]) / nb for i in range(0, 3)])
        if nb > 0
        else (0.0, 0.0, 0.0)
    )

    def mul(step, value):
        """Summary

        Parameters
        ----------
        step : TYPE
            Description
        value : TYPE
            Description

        Returns
        -------
        TYPE
            Description
        """
        return tuple([v * value for v in step])

    def add_v(step, step2):
        """Summary

        Parameters
        ----------
        step : TYPE
            Description
        step2 : TYPE
            Description

        Returns
        -------
        TYPE
            Description
        """
        return tuple([v + step2[i] for i, v in enumerate(step)])

    return [add_v(begin_hsl, mul(step, r)) for r in range(0, nb + 1)]


def hash_or_str(obj: object) -> int | str:
    """Summary

    Parameters
    ----------
    obj : object
        Description

    Returns
    -------
    int | str
        Description
    """
    try:
        return hash((type(obj).__name__, obj))
    except TypeError:
        # Adds the type name to make sure two objects of different type but
        # identical string representation get distinguished.
        return "\0".join([type(obj).__name__, str(obj)])


def format_last_exception(prefix: str = "  | ") -> str:
    """Format the last exception for display it in tests.

    This allows to raise custom exception, without loosing the context of what caused the problem
    in the first place.

    Parameters
    ----------
    prefix : str, optional
        Line prefix.

    Returns
    -------
    str
        Formatted exception.

    Examples
    --------

    >>> from python_utils.colour.future_colour import format_last_exception

    >>> def f():
    ...     raise Exception("Something terrible happened")
    >>> try:
    ...     f()
    ... except Exception:
    ...     formated_exception = format_last_exception()
    ...     raise ValueError('Oups, an error occurred:\\n%s'
    ...         % formated_exception)
    Traceback (most recent call last):
    ...
    ValueError: Oups, an error occurred:
      | Traceback (most recent call last):
    ...
      | Exception: Something terrible happened

    """

    return "\n".join(
        str(prefix + line) for line in traceback.format_exc().strip().split("\n")
    )
