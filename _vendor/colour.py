# -*- coding: utf-8 -*-
"""Typing.

Attributes
----------
InputColor3TupleType
    A value that can be a 3-tuple of :py:class:`float`, an :py:class:`int` or a :py:class:`str`.
InputColor4TupleType
    A value that can be a 4-tuple of :py:class:`float`, an :py:class:`int` or a :py:class:`str`.
OutputColor3TupleType
    A value that can be a 3-tuple of :py:class:`float`.
OutputColor4TupleType
    A value that can be a 4-tuple of :py:class:`float`.
RestrictedInputColor3TupleType
    A value that can be a 3-tuple of :py:class:`float` or an :py:class:`int`.

Note
----
The sub-classing of most of these custom types is to avoid the actual types to *blead through* to the
function signatures. Seeing a type like
``tuple[Union[float, int, str], Union[float, int, str], Union[float, int, str], Union[float, int, str]]``
in a function signature is more annoying than usefull.
"""
from __future__ import annotations


OutputColor3TupleType = tuple[float, float, float]
OutputColor4TupleType = tuple[float, float, float, float]
InputColor3TupleType = tuple[float | int | str, float | int | str, float | int | str]
InputColor4TupleType = tuple[
    float | int | str, float | int | str, float | int | str, float | int | str
]
RestrictedInputColor3TupleType = tuple[float | int, float | int, float | int]


class OutputColor3Tuple(OutputColor3TupleType):
    """A 3-tuple whose :py:class:`float` elements represent values for various of the supported color models.
    """


class OutputColor4Tuple(OutputColor4TupleType):
    """A 4-tuple whose :py:class:`float` elements represent values for the
    `CMYK <https://en.wikipedia.org/wiki/CMYK_color_model>`__ color model.
    """


class InputColor3Tuple(InputColor3TupleType):
    """A 3-tuple whose elements represent values for various of the supported color models
    and should be accepted as arguments for the :py:class:`float` built-in.
    """


class InputColor4Tuple(InputColor4TupleType):
    """A 4-tuple whose elements represent values for the
    `CMYK <https://en.wikipedia.org/wiki/CMYK_color_model>`__ color model.
    """


class RestrictedInputColor3Tuple(RestrictedInputColor3TupleType):
    """A 3-tuple whose elements can be accepted as arguments for :py:class:`future_colour.Matrix`.
    Each element is *restricted* to :py:class:`int` or :py:class:`float` types.
    """
