# -*- coding: utf-8 -*-
"""Color Library (https://github.com/vaab/colour).

This module defines several color formats that can be converted to one or another.

.. note::

    **Differences with upstream**

    - Removed runtime creation of the color names to RGB maps.

**Formats**

- `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__: A 3-tuple of Hue, Saturation, \
Lightness all between 0.0 and 1.0.
- `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__: A 3-tuple of Red, Green, \
Blue all between 0.0 and 1.0.
- `HEX <https://en.wikipedia.org/wiki/Web_colors>`__: A string object beginning with '#' and with \
red, green, blue value. This format accept color in 3 or 6 value ex: ``#fff`` or ``#ffffff``.
- `WEB <https://en.wikipedia.org/wiki/Web_colors>`__: A string object that defaults to \
`HEX <https://en.wikipedia.org/wiki/Web_colors>`__ representation or human if possible.

**Usage**

Several functions exist to convert from one format to another. But all functions are not written. \
So the best way is to use the object Color.

Please see the documentation of this object for more information.

.. note::

    Some constants are defined for convenience in :py:attr:`HSL`, :py:attr:`RGB`, :py:attr:`HEX`.

Attributes
----------
HEX
    `HEX <https://en.wikipedia.org/wiki/Web_colors>`__ colors container.
HSL
    `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__ colors container.
RGB
    `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ colors container.

"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._vendor.colour import InputColor3Tuple
    from .._vendor.colour import OutputColor3Tuple

import hashlib

from collections.abc import Callable

from .color_maps import RGB_TO_WEB_COLOR_NAMES
from .color_maps import WEB_COLOR_NAME_TO_RGB

from .constants import FLOAT_ERROR
from .constants import LONG_HEX_COLOR
from .constants import SHORT_HEX_COLOR

from .utils import color_scale
from .utils import hash_or_str
from .utils import hue2rgb
from .utils import sanitize_color_name


class C_HSL:
    """`HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__ colors container.

    Examples
    --------

    >>> from python_utils.colour import HSL

    >>> HSL.WHITE
    (0.0, 0.0, 1.0)
    >>> HSL.BLUE
    (0.6666666666666666, 1.0, 0.5)

    >>> HSL.DONOTEXISTS
    Traceback (most recent call last):
    ...
    AttributeError: ... has no attribute 'DONOTEXISTS'

    """

    def __getattr__(self, value):
        """See :py:meth:`object.__getattr__`.

        Parameters
        ----------
        value : str
            A color name.

        Returns
        -------
        OutputColor3Tuple
            `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__ representation of color name.

        Raises
        ------
        AttributeError
            Color name not on colors database.
        """
        label = sanitize_color_name(value)

        if label in WEB_COLOR_NAME_TO_RGB:
            return rgb2hsl(tuple(v / 255.0 for v in WEB_COLOR_NAME_TO_RGB[label]))

        raise AttributeError("%s instance has no attribute %r" % (self.__class__, value))


class C_RGB:
    """`RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ colors container.

    Provides a quick color access.

    Examples
    --------

    >>> from python_utils.colour import RGB

    >>> RGB.WHITE
    (1.0, 1.0, 1.0)
    >>> RGB.BLUE
    (0.0, 0.0, 1.0)

    >>> RGB.DONOTEXISTS
    Traceback (most recent call last):
    ...
    AttributeError: ... has no attribute 'DONOTEXISTS'

    """

    def __getattr__(self, value: str) -> OutputColor3Tuple:
        """See :py:meth:`object.__getattr__`.

        Parameters
        ----------
        value : str
            A color name.

        Returns
        -------
        OutputColor3Tuple
            `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ representation of color name.
        """
        return hsl2rgb(getattr(HSL, value))


class C_HEX:
    """`HEX <https://en.wikipedia.org/wiki/Web_colors>`__ colors container.

    Provides a quick color access.

    Examples
    --------

    >>> from python_utils.colour import HEX

    >>> HEX.WHITE
    '#fff'
    >>> HEX.BLUE
    '#00f'

    >>> HEX.DONOTEXISTS
    Traceback (most recent call last):
    ...
    AttributeError: ... has no attribute 'DONOTEXISTS'

    """

    def __getattr__(self, value: str) -> str:
        """See :py:meth:`object.__getattr__`.

        Parameters
        ----------
        value : str
            A color name.

        Returns
        -------
        str
            `HEX <https://en.wikipedia.org/wiki/Web_colors>`__ representation of color name.
        """
        return rgb2hex(getattr(RGB, value))


HSL: C_HSL = C_HSL()
RGB: C_RGB = C_RGB()
HEX: C_HEX = C_HEX()


##
# Conversion function
##


def hsl2rgb(hsl: InputColor3Tuple) -> OutputColor3Tuple:
    """Convert `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__
    representation towards `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__.

    Hue, Saturation, Range from Lightness is a float between 0 and 1.

    Note that Hue can be set to any value but as it is a rotation
    around the chromatic circle, any value above 1 or below 0 can
    be expressed by a value between 0 and 1 (Note that h=0 is equiv
    to h=1).

    This algorithm came from `EasyRGB <http://www.easyrgb.com/index.php?X=MATH&H=19#text19>`__

    Parameters
    ----------
    hsl : InputColor3Tuple
        Hue, position around the chromatic circle (h=1 equiv h=0).
        Saturation, color saturation (0=full gray, 1=full color).
        Lightness, Overhaul lightness (0=full black, 1=full white).

    Returns
    -------
    OutputColor3Tuple
        A 3-tuple for `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ values
        in float between 0 and 1.

    Raises
    ------
    ValueError
        Lightness/Saturation out of range. Must be between 0 and 1.

    Examples
    --------

    Here are some quick notion of `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__
    to `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ conversion

    >>> from python_utils.colour import hsl2rgb

    With a lightness put at 0, `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__
    is always rgbblack

    >>> hsl2rgb((0.0, 0.0, 0.0))
    (0.0, 0.0, 0.0)
    >>> hsl2rgb((0.5, 0.0, 0.0))
    (0.0, 0.0, 0.0)
    >>> hsl2rgb((0.5, 0.5, 0.0))
    (0.0, 0.0, 0.0)

    Same for lightness put at 1, `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__
    is always rgbwhite

    >>> hsl2rgb((0.0, 0.0, 1.0))
    (1.0, 1.0, 1.0)
    >>> hsl2rgb((0.5, 0.0, 1.0))
    (1.0, 1.0, 1.0)
    >>> hsl2rgb((0.5, 0.5, 1.0))
    (1.0, 1.0, 1.0)

    With saturation put at 0, the `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__
    should be equal to Lightness:

    >>> hsl2rgb((0.0, 0.0, 0.25))
    (0.25, 0.25, 0.25)
    >>> hsl2rgb((0.5, 0.0, 0.5))
    (0.5, 0.5, 0.5)
    >>> hsl2rgb((0.5, 0.0, 0.75))
    (0.75, 0.75, 0.75)

    With saturation put at 1, and lightness put to 0.5, we can find
    normal full red, green, blue colors:

    >>> hsl2rgb((0 , 1.0, 0.5))
    (1.0, 0.0, 0.0)
    >>> hsl2rgb((1 , 1.0, 0.5))
    (1.0, 0.0, 0.0)
    >>> hsl2rgb((1.0/3 , 1.0, 0.5))
    (0.0, 1.0, 0.0)
    >>> hsl2rgb((2.0/3 , 1.0, 0.5))
    (0.0, 0.0, 1.0)

    Of course

    >>> hsl2rgb((0.0, 2.0, 0.5))
    Traceback (most recent call last):
    ...
    ValueError: Saturation must be between 0 and 1.

    And

    >>> hsl2rgb((0.0, 0.0, 1.5))
    Traceback (most recent call last):
    ...
    ValueError: Lightness must be between 0 and 1.

    """
    h, s, l = [float(v) for v in hsl]  # noqa

    if not (0.0 - FLOAT_ERROR <= s <= 1.0 + FLOAT_ERROR):
        raise ValueError("Saturation must be between 0 and 1.")
    if not (0.0 - FLOAT_ERROR <= l <= 1.0 + FLOAT_ERROR):
        raise ValueError("Lightness must be between 0 and 1.")

    if s == 0:
        return l, l, l

    if l < 0.5:
        v2 = l * (1.0 + s)
    else:
        v2 = (l + s) - (s * l)

    v1 = 2.0 * l - v2

    r = hue2rgb(v1, v2, h + (1.0 / 3))
    g = hue2rgb(v1, v2, h)
    b = hue2rgb(v1, v2, h - (1.0 / 3))

    return r, g, b


def rgb2hsl(rgb: InputColor3Tuple) -> OutputColor3Tuple:
    """Convert `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ representation towards
    `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__.

    This algorithm came from `EasyRGB <http://www.easyrgb.com/index.php?X=MATH&H=19#text19>`__.

    Parameters
    ----------
    rgb : InputColor3Tuple
        Red amount (float between 0 and 1).
        Green amount (float between 0 and 1).
        Blue amount (float between 0 and 1).

    Returns
    -------
    OutputColor3Tuple
        3-tuple for `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__ values in float between 0 and 1.

    Raises
    ------
    ValueError
        Red/Green/Blue out of range. Must be between 0 and 1.

    Examples
    --------

    Here are some quick notion of `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__
    to `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__ conversion.

    >>> from python_utils.colour import rgb2hsl

    Note that if red amount is equal to green and blue, then you
    should have a gray value (from black to white).

    >>> rgb2hsl((1.0, 1.0, 1.0))
    (..., 0.0, 1.0)
    >>> rgb2hsl((0.5, 0.5, 0.5))
    (..., 0.0, 0.5)
    >>> rgb2hsl((0.0, 0.0, 0.0))
    (..., 0.0, 0.0)

    If only one color is different from the others, it defines the

    direct Hue

    >>> rgb2hsl((0.5, 0.5, 1.0))
    (0.66..., 1.0, 0.75)
    >>> rgb2hsl((0.2, 0.1, 0.1))
    (0.0, 0.33..., 0.15...)

    Having only one value set, you can check that:

    >>> rgb2hsl((1.0, 0.0, 0.0))
    (0.0, 1.0, 0.5)
    >>> rgb2hsl((0.0, 1.0, 0.0))
    (0.33..., 1.0, 0.5)
    >>> rgb2hsl((0.0, 0.0, 1.0))
    (0.66..., 1.0, 0.5)

    Regression check upon very close values in every component of
    red, green and blue:

    >>> rgb2hsl((0.9999999999999999, 1.0, 0.9999999999999994))
    (0.0, 0.0, 0.999...)

    Of course

    >>> rgb2hsl((0.0, 2.0, 0.5))
    Traceback (most recent call last):
    ...
    ValueError: Green must be between 0 and 1. You provided 2.0.

    And

    >>> rgb2hsl((0.0, 0.0, 1.5))
    Traceback (most recent call last):
    ...
    ValueError: Blue must be between 0 and 1. You provided 1.5.

    """
    r, g, b = [float(v) for v in rgb]

    for name, v in {"Red": r, "Green": g, "Blue": b}.items():
        if not (0 - FLOAT_ERROR <= v <= 1 + FLOAT_ERROR):
            raise ValueError("%s must be between 0 and 1. You provided %r." % (name, v))

    vmin = min(r, g, b)  # Min. value of RGB
    vmax = max(r, g, b)  # Max. value of RGB
    diff = vmax - vmin  # Delta RGB value

    vsum = vmin + vmax

    l = vsum / 2  # noqa

    if diff < FLOAT_ERROR:  # This is a gray, no chroma...
        return (0.0, 0.0, l)

    ##
    # Chromatic data...
    ##

    # Saturation
    if l < 0.5:
        s = diff / vsum
    else:
        s = diff / (2.0 - vsum)

    dr = (((vmax - r) / 6) + (diff / 2)) / diff
    dg = (((vmax - g) / 6) + (diff / 2)) / diff
    db = (((vmax - b) / 6) + (diff / 2)) / diff

    if r == vmax:
        h = db - dg
    elif g == vmax:
        h = (1.0 / 3) + dr - db
    elif b == vmax:
        h = (2.0 / 3) + dg - dr

    if h < 0:
        h += 1
    if h > 1:
        h -= 1

    return (h, s, l)


def rgb2hex(
    rgb: InputColor3Tuple,
    force_long: bool = False,
) -> str:
    """Transform `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__
    tuple to hex `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ representation

    Parameters
    ----------
    rgb : InputColor3Tuple
        `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ 3-tuple of floats between 0 and 1.
    force_long : bool, optional
        Force 6 digits representation of `HEX <https://en.wikipedia.org/wiki/Web_colors>`__ color.

    Returns
    -------
    str
        A 3 hexadecimal characters or 6 hexadecimal characters string representation.

    Examples
    --------

    >>> from python_utils.colour import rgb2hex
    >>> rgb2hex((0.0,1.0,0.0))
    '#0f0'

    Rounding try to be as natural as possible:

    >>> rgb2hex((0.0,0.999999,1.0))
    '#0ff'

    And if not possible, the 6 hex char representation is used:

    >>> rgb2hex((0.23,1.0,1.0))
    '#3bffff'

    >>> rgb2hex((0.0,0.999999,1.0), force_long=True)
    '#00ffff'

    """

    hx = "".join(["%02x" % int(c * 255 + 0.5 - FLOAT_ERROR) for c in rgb])

    if not force_long and hx[0::2] == hx[1::2]:
        hx = "".join(hx[0::2])

    return "#%s" % hx


def hex2rgb(str_rgb: str) -> OutputColor3Tuple:
    """Transform hex `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__
    representation to `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ tuple.

    Parameters
    ----------
    str_rgb : str
        A 3 hexadecimal characters or 6 hexadecimal characters string representation.

    Returns
    -------
    OutputColor3Tuple
        `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ 3-tuple of floats between 0 and 1.

    Raises
    ------
    ValueError
        Invalid `HEX <https://en.wikipedia.org/wiki/Web_colors>`__ representation of color.

    Examples
    --------

    >>> from python_utils.colour import hex2rgb

    >>> hex2rgb('#00ff00')
    (0.0, 1.0, 0.0)

    >>> hex2rgb('#0f0')
    (0.0, 1.0, 0.0)

    >>> hex2rgb('#aaa')
    (0.66..., 0.66..., 0.66...)

    >>> hex2rgb('#aa')
    Traceback (most recent call last):
    ...
    ValueError: Invalid value '#aa' provided for rgb color.

    """

    try:
        rgb = str_rgb[1:]

        if len(rgb) == 6:
            r, g, b = rgb[0:2], rgb[2:4], rgb[4:6]
        elif len(rgb) == 3:
            r, g, b = rgb[0] * 2, rgb[1] * 2, rgb[2] * 2
        else:
            raise ValueError()
    except BaseException:
        raise ValueError("Invalid value %r provided for rgb color." % str_rgb)

    return tuple([float(int(v, 16)) / 255 for v in (r, g, b)])


def hex2web(hex: str) -> str:
    """Converts `HEX <https://en.wikipedia.org/wiki/Web_colors>`__ representation
    to `WEB <https://en.wikipedia.org/wiki/Web_colors>`__.

    `WEB <https://en.wikipedia.org/wiki/Web_colors>`__ representation uses X11 rgb.txt to
    define conversion between `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__
    and English color names.

    Parameters
    ----------
    hex : str
        A 3 hexadecimal characters or 6 hexadecimal characters string representation

    Returns
    -------
    str
        Web string representation (human readable if possible).

    Examples
    --------

    >>> from python_utils.colour import hex2web

    >>> hex2web('#ff0000')
    'red'

    >>> hex2web('#aaaaaa')
    '#aaa'

    >>> hex2web('#abc')
    '#abc'

    >>> hex2web('#acacac')
    '#acacac'

    """
    dec_rgb = tuple(int(v * 255) for v in hex2rgb(hex))
    if dec_rgb in RGB_TO_WEB_COLOR_NAMES:
        return RGB_TO_WEB_COLOR_NAMES[dec_rgb][0]

    # Hex format is verified by hex2rgb function. And should be 3 or 6 digit
    if len(hex) == 7:
        if hex[1] == hex[2] and hex[3] == hex[4] and hex[5] == hex[6]:
            return "#" + hex[1] + hex[3] + hex[5]
    return hex


def web2hex(web: str, force_long: bool = False) -> str:
    """Converts `WEB <https://en.wikipedia.org/wiki/Web_colors>`__ representation to
    `HEX <https://en.wikipedia.org/wiki/Web_colors>`__

    `WEB <https://en.wikipedia.org/wiki/Web_colors>`__ representation uses X11 rgb.txt to
    define conversion between `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__
    and English color names.

    Parameters
    ----------
    web : str
        Web string representation (human readable if possible).
    force_long : bool, optional
        Force 6 digits representation of `HEX <https://en.wikipedia.org/wiki/Web_colors>`__ color.

    Returns
    -------
    str
        A 3 hexadecimal characters or 6 hexadecimal characters string representation.

    Raises
    ------
    AttributeError
        Invalid `HEX <https://en.wikipedia.org/wiki/Web_colors>`__ representation of color.
    ValueError
        Color name not in colors database.

    Examples
    --------

    >>> from python_utils.colour import web2hex

    >>> web2hex('red')
    '#f00'

    >>> web2hex('#aaa')
    '#aaa'

    >>> web2hex('#foo')
    Traceback (most recent call last):
    ...
    AttributeError: '#foo' is not in web format. Need 3 or 6 hex digit.

    >>> web2hex('#aaa', force_long=True)
    '#aaaaaa'

    >>> web2hex('#aaaaaa')
    '#aaaaaa'

    >>> web2hex('#aaaa')
    Traceback (most recent call last):
    ...
    AttributeError: '#aaaa' is not in web format. Need 3 or 6 hex digit.

    >>> web2hex('pinky')
    Traceback (most recent call last):
    ...
    ValueError: 'pinky' is not a recognized color.

    And color names are case insensitive

    >>> from python_utils.colour import Color
    >>> Color('RED')
    <Color red>

    """
    if web.startswith("#"):
        if LONG_HEX_COLOR.match(web) or (not force_long and SHORT_HEX_COLOR.match(web)):
            return web.lower()
        elif SHORT_HEX_COLOR.match(web) and force_long:
            return "#" + "".join([("%s" % (t,)) * 2 for t in web[1:]])
        raise AttributeError("%r is not in web format. Need 3 or 6 hex digit." % web)

    web = sanitize_color_name(web)
    if web not in WEB_COLOR_NAME_TO_RGB:
        raise ValueError("%r is not a recognized color." % web)

    # convert dec to hex:

    return rgb2hex([float(int(v)) / 255 for v in WEB_COLOR_NAME_TO_RGB[web]], force_long)


# Missing functions conversion


def hsl2hex(x: InputColor3Tuple) -> str:
    """`HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__ to
    `HEX <https://en.wikipedia.org/wiki/Web_colors>`__ conversion.

    Parameters
    ----------
    x : InputColor3Tuple
        `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__ color.

    Returns
    -------
    str
        `HEX <https://en.wikipedia.org/wiki/Web_colors>`__ color.
    """
    return rgb2hex(hsl2rgb(x))


def hex2hsl(x: str) -> OutputColor3Tuple:
    """`HEX <https://en.wikipedia.org/wiki/Web_colors>`__ to
    `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__ conversion.

    Parameters
    ----------
    x : str
        `HEX <https://en.wikipedia.org/wiki/Web_colors>`__ color.

    Returns
    -------
    OutputColor3Tuple
        `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__ color.
    """
    return rgb2hsl(hex2rgb(x))


def rgb2web(x: InputColor3Tuple) -> str:
    """`RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ to web conversion.

    Parameters
    ----------
    x : InputColor3Tuple
        `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ color.

    Returns
    -------
    str
        Web color.
    """
    return hex2web(rgb2hex(x))


def web2rgb(x: str) -> OutputColor3Tuple:
    """Web to `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ conversion.

    Parameters
    ----------
    x : str
        Web color.

    Returns
    -------
    OutputColor3Tuple
        `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ color.
    """
    return hex2rgb(web2hex(x))


def web2hsl(x: str) -> OutputColor3Tuple:
    """Web to `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__ conversion.

    Parameters
    ----------
    x : str
        Web color

    Returns
    -------
    OutputColor3Tuple
        `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__ color.
    """
    return rgb2hsl(web2rgb(x))


def hsl2web(x: InputColor3Tuple) -> str:
    """`HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__ to web conversion.

    Parameters
    ----------
    x : InputColor3Tuple
        `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__ color.

    Returns
    -------
    str
        Web color.
    """
    return rgb2web(hsl2rgb(x))


##
# Color Pickers
##


def RGB_color_picker(obj: object) -> Color:
    """Build a color representation from the string representation of an object

    Parameters
    ----------
    obj : object
        Description

    Returns
    -------
    Color
        Description

    Examples
    --------

    This allows to quickly get a color from some data, with the
    additional benefit that the color will be the same as long as the
    (string representation of the) data is the same:

    >>> from python_utils.colour import RGB_color_picker, Color

    Same inputs produce the same result:

    >>> RGB_color_picker("Something") == RGB_color_picker("Something")
    True

    ...but different inputs produce different colors:

    >>> RGB_color_picker("Something") != RGB_color_picker("Something else")
    True

    In any case, we still get a ``Color`` object:

    >>> isinstance(RGB_color_picker("Something"), Color)
    True

    """

    # Turn the input into a by 3-dividable string. SHA-384 is good because it
    # divides into 3 components of the same size, which will be used to
    # represent the RGB values of the color.
    digest = hashlib.sha384(str(obj).encode("utf-8")).hexdigest()

    # Split the digest into 3 sub-strings of equivalent size.
    subsize = int(len(digest) / 3)
    splitted_digest = [digest[i * subsize: (i + 1) * subsize] for i in range(3)]

    # Convert those hexadecimal sub-strings into integer and scale them down
    # to the 0..1 range.
    max_value = float(int("f" * subsize, 16))
    components = (
        int(d, 16)  # Make a number from a list with hex digits
        / max_value  # Scale it down to [0.0, 1.0]
        for d in splitted_digest
    )

    return Color(rgb2hex(components))  # Profit!


##
# All purpose object
##


class Color(object):
    """Abstraction of a color object.

    Attributes
    ----------
    equality : TYPE
        Description
    hex : TYPE
        Description
    hsl : TYPE
        Description
    rgb : TYPE
        Description
    web : TYPE
        Description

    Examples
    --------

    Color object keeps information of a color. It can input/output to different
    format (`HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__,
    `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__,
    `HEX <https://en.wikipedia.org/wiki/Web_colors>`__,
    `WEB <https://en.wikipedia.org/wiki/Web_colors>`__) and their partial representation.

    >>> from python_utils.colour import Color, HSL

    >>> b = Color()
    >>> b.hsl = HSL.BLUE

    Access values

    >>> b.hue
    0.66...
    >>> b.saturation
    1.0
    >>> b.luminance
    0.5

    >>> b.red
    0.0
    >>> b.blue
    1.0
    >>> b.green
    0.0

    >>> b.rgb
    (0.0, 0.0, 1.0)
    >>> b.hsl
    (0.66..., 1.0, 0.5)
    >>> b.hex
    '#00f'

    Change values

    Let's change Hue toward red tint:

    >>> b.hue = 0.0
    >>> b.hex
    '#f00'

    >>> b.hue = 2.0/3
    >>> b.hex
    '#00f'

    In the other way round:

    >>> b.hex = '#f00'
    >>> b.hsl
    (0.0, 1.0, 0.5)

    Long hex can be accessed directly:

    >>> b.hex_l = '#123456'
    >>> b.hex_l
    '#123456'
    >>> b.hex
    '#123456'

    >>> b.hex_l = '#ff0000'
    >>> b.hex_l
    '#ff0000'
    >>> b.hex
    '#f00'

    Convenience

    >>> c = Color('blue')
    >>> c
    <Color blue>
    >>> c.hue = 0
    >>> c
    <Color red>

    >>> c.saturation = 0.0
    >>> c.hsl
    (..., 0.0, 0.5)
    >>> c.rgb
    (0.5, 0.5, 0.5)
    >>> c.hex
    '#7f7f7f'
    >>> c
    <Color #7f7f7f>

    >>> c.luminance = 0.0
    >>> c
    <Color black>

    >>> c.hex
    '#000'

    >>> c.green = 1.0
    >>> c.blue = 1.0
    >>> c.hex
    '#0ff'
    >>> c
    <Color aqua>

    >>> c = Color('blue', luminance=0.75)
    >>> c
    <Color #7f7fff>

    >>> c = Color('red', red=0.5)
    >>> c
    <Color #7f0000>

    >>> print(c)
    #7f0000

    You can try to query non-existing attributes:

    >>> c.lightness
    Traceback (most recent call last):
    ...
    AttributeError: 'lightness' not found

    **Recursive initialization**

    To support blind conversion of web strings (or already converted object),
    the Color object supports instantiation with another Color object.

    >>> Color(Color(Color('red')))
    <Color red>

    **Equality support**

    Default equality is `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ hex comparison:

    >>> Color('red') == Color('blue')
    False
    >>> Color('red') == Color('red')
    True
    >>> Color('red') != Color('blue')
    True
    >>> Color('red') != Color('red')
    False

    But this can be changed:

    >>> saturation_equality = lambda c1, c2: c1.luminance == c2.luminance
    >>> Color('red', equality=saturation_equality) == Color('blue')
    True

    **Sub-classing support**

    You should be able to subclass ``Color`` object without any issues:

    >>> class Tint(Color):
    ...     pass

    And keep the internal API working:

    >>> Tint("red").hsl
    (0.0, 1.0, 0.5)

    Todo
    ----
    Could add HSV, CMYK, YUV conversion.

    >>> b.hsv            # doctest: +SKIP
    >>> b.value          # doctest: +SKIP
    >>> b.cyan           # doctest: +SKIP
    >>> b.magenta        # doctest: +SKIP
    >>> b.yellow         # doctest: +SKIP
    >>> b.key            # doctest: +SKIP
    >>> b.cmyk           # doctest: +SKIP

    """

    _hsl = None  # internal representation

    def __init__(
        self,
        color: str = None,
        pick_for=None,
        picker: Callable[..., Color] = RGB_color_picker,
        pick_key: Callable[[object], int | str] = hash_or_str,
        **kwargs,
    ):
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        color : str, optional
            Description
        pick_for : None, optional
            Description
        picker : Callable[..., Color], optional
            Description
        pick_key : Callable[[object], int | str], optional
            Description
        **kwargs
            Description

        Returns
        -------
        TYPE
            Description
        """
        if pick_key is None:

            def pick_key(x):
                """Summary

                Parameters
                ----------
                x : TYPE
                    Description

                Returns
                -------
                TYPE
                    Description
                """
                return x

        if pick_for is not None:
            color = picker(pick_key(pick_for))

        if isinstance(color, Color):
            self.web = color.web
        else:
            self.web = color if color else "black"

        self.equality = RGB_equivalence

        for k, v in kwargs.items():
            setattr(self, k, v)

    def __getattr__(self, label):
        """See :py:meth:`object.__getattr__`.

        Parameters
        ----------
        label : TYPE
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
        if label.startswith("get_"):
            raise AttributeError("'%s' not found" % label)
        try:
            return getattr(self, "get_" + label)()
        except AttributeError:
            raise AttributeError("'%s' not found" % label)

    def __setattr__(self, label, value):
        """See :py:meth:`object.__setattr__`.

        Parameters
        ----------
        label : TYPE
            Description
        value : TYPE
            Description
        """
        if label not in ["_hsl", "equality"]:
            fc = getattr(self, "set_" + label)
            fc(value)
        else:
            self.__dict__[label] = value

    ##
    # Get
    ##

    def get_hsl(self):
        """Summary

        Returns
        -------
        TYPE
            Description
        """
        return tuple(self._hsl)

    def get_hex(self):
        """Summary

        Returns
        -------
        TYPE
            Description
        """
        return rgb2hex(self.rgb)

    def get_hex_l(self):
        """Summary

        Returns
        -------
        TYPE
            Description
        """
        return rgb2hex(self.rgb, force_long=True)

    def get_rgb(self):
        """Summary

        Returns
        -------
        TYPE
            Description
        """
        return hsl2rgb(self.hsl)

    def get_hue(self):
        """Summary

        Returns
        -------
        TYPE
            Description
        """
        return self.hsl[0]

    def get_saturation(self):
        """Summary

        Returns
        -------
        TYPE
            Description
        """
        return self.hsl[1]

    def get_luminance(self):
        """Summary

        Returns
        -------
        TYPE
            Description
        """
        return self.hsl[2]

    def get_red(self):
        """Summary

        Returns
        -------
        TYPE
            Description
        """
        return self.rgb[0]

    def get_green(self):
        """Summary

        Returns
        -------
        TYPE
            Description
        """
        return self.rgb[1]

    def get_blue(self):
        """Summary

        Returns
        -------
        TYPE
            Description
        """
        return self.rgb[2]

    def get_web(self):
        """Summary

        Returns
        -------
        TYPE
            Description
        """
        return hex2web(self.hex)

    ##
    # Set
    ##

    def set_hsl(self, value):
        """Summary

        Parameters
        ----------
        value : TYPE
            Description
        """
        self._hsl = list(value)

    def set_rgb(self, value):
        """Summary

        Parameters
        ----------
        value : TYPE
            Description
        """
        self.hsl = rgb2hsl(value)

    def set_hue(self, value):
        """Summary

        Parameters
        ----------
        value : TYPE
            Description
        """
        self._hsl[0] = value

    def set_saturation(self, value):
        """Summary

        Parameters
        ----------
        value : TYPE
            Description
        """
        self._hsl[1] = value

    def set_luminance(self, value):
        """Summary

        Parameters
        ----------
        value : TYPE
            Description
        """
        self._hsl[2] = value

    def set_red(self, value):
        """Summary

        Parameters
        ----------
        value : TYPE
            Description
        """
        _, g, b = self.rgb
        self.rgb = (value, g, b)

    def set_green(self, value):
        """Summary

        Parameters
        ----------
        value : TYPE
            Description
        """
        r, _, b = self.rgb
        self.rgb = (r, value, b)

    def set_blue(self, value):
        """Summary

        Parameters
        ----------
        value : TYPE
            Description
        """
        r, g, _ = self.rgb
        self.rgb = (r, g, value)

    def set_hex(self, value):
        """Summary

        Parameters
        ----------
        value : TYPE
            Description
        """
        self.rgb = hex2rgb(value)

    def set_hex_l(self, value):
        """Summary

        Parameters
        ----------
        value : TYPE
            Description
        """
        self.set_hex(value)

    def set_web(self, value):
        """Summary

        Parameters
        ----------
        value : TYPE
            Description
        """
        self.hex = web2hex(value)

    # range of color generation

    def range_to(self, value, steps):
        """Summary

        Parameters
        ----------
        value : TYPE
            Description
        steps : TYPE
            Description

        Yields
        ------
        TYPE
            Description
        """
        for hsl in color_scale(self._hsl, Color(value).hsl, steps - 1):
            yield Color(hsl=hsl)

    ##
    # Convenience
    ##

    def __str__(self):
        """See :py:meth:`object.__str__`.

        Returns
        -------
        TYPE
            Description
        """
        return "%s" % self.web

    def __repr__(self):
        """See :py:meth:`object.__repr__`.

        Returns
        -------
        TYPE
            Description
        """
        return "<Color %s>" % self.web

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
        if isinstance(other, Color):
            return self.equality(self, other)
        return NotImplemented


class Colour(Color):
    """Class equivalent to :py:class:`Color` class to add consistency with the name of the module.

    >>> from python_utils.colour import Colour, Color

    >>> red = Colour("red")
    >>> isinstance(red, Color)
    True
    """


def RGB_equivalence(c1, c2):
    """Summary

    Parameters
    ----------
    c1 : TYPE
        Description
    c2 : TYPE
        Description

    Returns
    -------
    TYPE
        Description
    """
    return c1.hex_l == c2.hex_l


def HSL_equivalence(c1, c2):
    """Summary

    Parameters
    ----------
    c1 : TYPE
        Description
    c2 : TYPE
        Description

    Returns
    -------
    TYPE
        Description
    """
    return c1._hsl == c2._hsl


def make_color_factory(**kwargs_defaults):
    """Summary

    Parameters
    ----------
    **kwargs_defaults
        Description

    Returns
    -------
    TYPE
        Description
    """

    def ColorFactory(*args, **kwargs):
        """Summary

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
        """
        new_kwargs = kwargs_defaults.copy()
        new_kwargs.update(kwargs)
        return Color(*args, **new_kwargs)

    return ColorFactory
