# -*- coding: utf-8 -*-
"""Color library.

.. note::

    This module is the non-released `rc1 <https://github.com/vaab/colour/tree/rc1>`__ branch of this
    library. I didn't directly implemented it into my fork because the API is completely different
    and I can barely understand through the trillion layers of abstraction/obfuscation its inner
    workings have (it will be a bitch to annotate/document). I added it just because it supports
    a lot more color formats.

    **Differences with upstream**

    - Added `X11 numbered variants <https://en.wikipedia.org/wiki/X11_color_names#Numbered_variants>`__.
    - Added `X11 100 shades of gray <https://en.wikipedia.org/wiki/X11_color_names#Shades_of_gray>`__.
    - Removed runtime creation of the color names to RGB maps.

This module defines several color formats that can be converted to one or another.

Several functions exist to convert from one format to another. But all
conversion functions are not written from all formats towards all formats.
By using :py:class:`Color`, you'll silently use all available functions, sometimes
chained, to give you a conversion from any format to any other.

Attributes
----------
Converters
    Converters registry.
Formats
    Formats registry.
RGB_TO_YUV
    `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ to
    `YUV <https://en.wikipedia.org/wiki/YUV>`__ conversion matrix.
YUV_TO_RGB
    `YUV <https://en.wikipedia.org/wiki/YUV>`__ to
    `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ conversion matrix.

"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._vendor.colour import InputColor3Tuple
    from .._vendor.colour import InputColor4Tuple
    from .._vendor.colour import OutputColor3Tuple
    from .._vendor.colour import OutputColor4Tuple
    from .._vendor.colour import RestrictedInputColor3Tuple
    from collections.abc import Callable
    from typing import Any

import colorsys
import hashlib
import inspect
import re

from collections import namedtuple

from .color_maps import RGB_TO_WEB_COLOR_NAMES
from .color_maps import RGB_TO_X11_COLOR_NAMES
from .color_maps import WEB_COLOR_NAME_TO_RGB
from .color_maps import X11_COLOR_NAME_TO_RGB

from .constants import FLOAT_ERROR
from .constants import LONG_HEX_COLOR
from .constants import SHORT_OR_LONG_HEX_COLOR

from .utils import color_scale
from .utils import format_last_exception
from .utils import hash_or_str
from .utils import hue2rgb
from .utils import sanitize_color_name
from .utils import with_metaclass


##
# Color Type Factory machinery
##


class FormatRegistry(list):
    """Summary"""

    def get(self, label, default=None):
        """Summary

        Parameters
        ----------
        label : TYPE
            Description
        default : None, optional
            Description

        Returns
        -------
        TYPE
            Description
        """
        for f in self:
            if label == str(f):
                return f
        return default

    def find(self, label):
        """Summary

        Parameters
        ----------
        label : TYPE
            Description

        Returns
        -------
        TYPE
            Description
        """
        f = self.get(label, None)
        if f is not None:
            return f, None
        return self.get_by_attr(label)

    def get_by_attr(self, label):
        """Summary

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
        ValueError
            Description
        """
        if "_" in label:
            format, label = label.split("_", 1)
            f = self.get(format, None)
            formats = [] if f is None else [f]
        else:
            formats = list(self)
        ret = []
        for f in formats:
            for attr in getattr(f, "_fields", []):
                if label == attr:
                    ret.append(f)
        if len(ret) > 1:
            raise ValueError(
                "Ambiguous attribute %r. Try one of: %s"
                % (label, ", ".join("%s_%s" % (f, label) for f in ret))
            )
        elif len(ret) == 1:
            return ret[0], label
        else:  # len(ret) == 0:
            return None, None


def register_format(
    registry: FormatRegistry,
) -> Callable[[Callable[[object], object]], object]:
    """Summary

    Parameters
    ----------
    registry : FormatRegistry
        Description

    Returns
    -------
    Callable[Callable[object, object], object]
        Description
    """

    def wrap(f: Callable[[object], object]) -> Callable[[object], object]:
        """Summary

        Parameters
        ----------
        f : Callable[object, object]
            Description

        Returns
        -------
        Callable[object, object]
            Description
        """
        registry.append(f)
        return f

    return wrap


class MetaFormat(type):
    """Summary"""

    def __getattr__(self, value: str):
        """See :py:meth:`object.__getattr__`.

        Parameters
        ----------
        value : str
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
        label = sanitize_color_name(value)

        if label in WEB_COLOR_NAME_TO_RGB:
            return RGB(tuple(v / 255.0 for v in WEB_COLOR_NAME_TO_RGB[label])).convert(self)

        if label in X11_COLOR_NAME_TO_RGB:
            return RGB(tuple(v / 255.0 for v in X11_COLOR_NAME_TO_RGB[label])).convert(self)

        raise AttributeError("%s instance has no attribute %r" % (self.__class__, value))

    def __repr__(self):
        """See :py:meth:`object.__repr__`.

        Returns
        -------
        TYPE
            Description
        """
        return "<Format %s>" % (self.__name__,)

    def __str__(self):
        """See :py:meth:`object.__str__`.

        Returns
        -------
        TYPE
            Description
        """
        return self.__name__.lower()


@with_metaclass(MetaFormat)
class Format(object):
    """Summary"""

    def convert(self, dst_format: str, converter_registry: ConverterRegistry = None):
        """Summary

        Parameters
        ----------
        dst_format : str
            Description
        converter_registry : ConverterRegistry, optional
            Description

        Returns
        -------
        TYPE
            Description
        """
        converter_registry = converter_registry or Converters
        src_format = type(self)
        ret = converter_registry.convert_fun(src_format, dst_format)(self)
        return ret


def Tuple(*a):
    """Create a simpler named tuple type, inheriting from ``Format``.

    Parameters
    ----------
    *a
        Description

    Returns
    -------
    TYPE
        Description

    Examples
    --------

    >>> from python_utils.colour.future_colour import Tuple, Format

    >>> Tuple("a", "b", "c")
    <Format Tuple(a, b, c)>

    This can conveniently be used as a parent class for formats, with
    an easy declaration:

    >>> class MyFormat(Tuple("a", "b", "c")): pass

    ...sensible representation:

    >>> MyFormat(1, 2, 3)
    MyFormat(a=1, b=2, c=3)

    ...and the ability to take a real tuple upon initialization:

    >>> MyFormat((1, 2, 3))
    MyFormat(a=1, b=2, c=3)

    ...keeping the awesome feature of :py:class:`collections.namedtuple`, a partial argument
    and keyword list:

    >>> MyFormat(1, b=2, c=3)
    MyFormat(a=1, b=2, c=3)

    Of course, these are subclasses of ``Format``:

    >>> isinstance(MyFormat((1, 2, 3)), Format)
    True

    """

    class klass(namedtuple("_Anon", a), Format):
        """Summary"""

        # Allow the support of instantiating with a single tuple.
        def __new__(cls, *a, **kw):
            """See :py:meth:`object.__new__`.

            Parameters
            ----------
            *a
                Description
            **kw
                Description

            Returns
            -------
            TYPE
                Description
            """
            if len(a) == 1 and isinstance(a[0], tuple) and len(a[0]) == len(cls._fields):
                return cls.__new__(cls, *a[0], **kw)
            return super(klass, cls).__new__(cls, *a, **kw)

        # Force namedtuple to read the actual name of the class
        def __repr__(self):
            """See :py:meth:`object.__repr__`.

            Returns
            -------
            TYPE
                Description
            """
            return "%s(%s)" % (
                self.__class__.__name__,
                ", ".join("%s=%r" % (f, getattr(self, f)) for f in self._fields),
            )

    # Provide a sensible name
    klass.__name__ = "Tuple(%s)" % (", ".join(a),)

    return klass


class String(str, Format):
    """Defines a Format based on Python string.

    Attributes
    ----------
    default : TYPE
        Description
    regex : TYPE
        Description

    Examples
    --------

    A default validation will be done on the class attribute ``regex``:

    >>> import re
    >>> from python_utils.colour.future_colour import String
    >>> class MyFormat(String):
    ...     regex = re.compile('(red|blue|green)')
    >>> MyFormat('invalid')
    Traceback (most recent call last):
    ...
    ValueError: Invalid string specifier 'invalid' format for MyFormat format.
    >>> red = MyFormat('red')
    >>> red
    'red'

    Notice that the representation of this object is invisible as it
    is a subclass of string.

    Although:

    >>> type(MyFormat('red'))
    <Format MyFormat>

    You can avoid setting ``regex`` if you have no use of this check:

    >>> class MyFormat(String): pass
    >>> MyFormat('red')
    'red'

    """

    default = None  # no value
    regex = None

    def __new__(cls, s: str, **kwargs):
        """See :py:meth:`object.__new__`.

        Parameters
        ----------
        s : str
            Description
        **kwargs
            Description

        Returns
        -------
        TYPE
            Description
        """
        if s is None and cls.default is not None:
            s = cls.default
        s = cls._validate(s)
        return super(String, cls).__new__(cls, s)

    @classmethod
    def _validate(cls, s: str):
        """Summary

        Parameters
        ----------
        s : str
            Description

        Returns
        -------
        TYPE
            Description

        Raises
        ------
        ValueError
            Description
        """
        if cls.regex:
            if not cls.regex.match(s):
                raise ValueError(
                    "Invalid string specifier %r format for %s format." % (s, cls.__name__)
                )
        return s


##
# Converters function
##


class ConverterRegistry(list):
    """Provides helper functions to get and combine converters function.

    Examples
    --------

    First, this object acts as a registry, storing in a list the available
    converters. Converters are special annotated functions:

    >>> from python_utils.colour.future_colour import ConverterRegistry, register_converter
    >>> cr = ConverterRegistry()

    Registering should be done thanks to ``register_converter`` decorator:

    >>> @register_converter(cr, src="hex", dst="dec")
    ... def hex2dec(x): return int(x, 16)

    Or equivalently:

    >>> register_converter(cr, src="dec", dst="hex")(
    ...     lambda x: hex(x))
    <function <lambda> at ...>
    >>> register_converter(cr, src="dec", dst="bin")(
    ...     lambda x: bin(x))
    <function <lambda> at ...>

    Then we can expect simply converting between available path:

    >>> cr.convert_fun("hex", "dec")("15")
    21

    The most convenient way to access converters is to use the
    'xxx2yyy' attributes of a ``ConverterRegistry``, so the last
    instruction is equivalent to:

    >>> cr.hex2dec("15")
    21

    Note that this is provided directly by only one converter, in the following
    2 converters will be used to get to the answer:

    >>> cr.hex2bin("15")
    '0b10101'

    When source and destination format are equivalent, this will make not change
    on the output:

    >>> cr.hex2hex("15")
    '15'

    And if no path exists it'll cast an exception:

    >>> cr.bin2hex("0101")
    Traceback (most recent call last):
    ...
    ValueError: No conversion path found from bin to hex format.

    If one of the 2 part of 'xxx2yyy' is not a valid format label,
    it will complain:

    >>> cr.foo2hex("0101")
    Traceback (most recent call last):
    ...
    AttributeError: Unknown format labeled foo.

    >>> cr.hex2foo("0101")
    Traceback (most recent call last):
    ...
    AttributeError: Unknown format labeled foo.

    If not a 'xxx2yyy' format, it'll cast normal attribute error:

    >>> cr.foo("0101")
    Traceback (most recent call last):
    ...
    AttributeError: no attribute 'foo'

    Note that if the functions have already been annotated, then you
    can instantiate directly a new ``ConverterRegistry``:

    >>> new_cr = ConverterRegistry(cr)
    >>> new_cr.hex2bin("15")
    '0b10101'

    """

    def __init__(self, converters=None):
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        converters : None, optional
            Description
        """
        if converters is None:
            converters = []
        super(ConverterRegistry, self).__init__(converters)

    @property
    def formats(self):
        """Summary

        Returns
        -------
        TYPE
            Description
        """

        def i():
            """Summary

            Yields
            ------
            TYPE
                Description
            """
            for cv in self:
                yield cv.src
                yield cv.dst

        return set(i())

    def get(self, src):
        """Summary

        Parameters
        ----------
        src : TYPE
            Description

        Returns
        -------
        TYPE
            Description
        """
        return {cv.dst: (cv, cv.conv_kwargs) for cv in self if cv.src is src}

    def find_path(self, src, dst):
        """Summary

        Parameters
        ----------
        src : TYPE
            Description
        dst : TYPE
            Description

        Returns
        -------
        TYPE
            Description
        """
        visited = [src]
        nexts = [(([], n), t[0], t[1]) for n, t in self.get(src).items() if n not in visited]
        while len(nexts) != 0:
            (path, next), fun, dct = nexts.pop()
            visited.append(next)
            new_path = path + [fun]
            dsts = self.get(next)
            if dst is next:
                return new_path
            nexts.extend([((new_path, n), t[0], t[1]) for n, t in dsts.items() if n not in visited])

    def convert_fun(self, src_format, dst_format):
        """Summary

        Parameters
        ----------
        src_format : TYPE
            Description
        dst_format : TYPE
            Description

        Returns
        -------
        TYPE
            Description

        Raises
        ------
        ValueError
            Description
        """

        def _path_to_callable(path):
            """Summary

            Parameters
            ----------
            path : TYPE
                Description

            Returns
            -------
            TYPE
                Description
            """

            def _f(value):
                """Summary

                Parameters
                ----------
                value : TYPE
                    Description

                Returns
                -------
                TYPE
                    Description
                """
                for fun in path:
                    value = fun(value)
                    if callable(fun.dst):
                        value = fun.dst(value)
                return value

            return _f

        if src_format is dst_format or src_format == dst_format:
            return lambda x: x
        path = self.find_path(src_format, dst_format)
        if path:
            return _path_to_callable(path)
        path = self.find_path(src_format, dst_format)
        raise ValueError(
            "No convertion path found from %s to %s format." % (src_format, dst_format)
        )

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
        m = re.match(r"(?P<src>[a-zA-Z0-9_]+)2(?P<dst>[a-zA-Z0-9_]+)", label)
        if m is None:
            raise AttributeError("no attribute %r" % (label,))
        dct = m.groupdict()
        for target, label in list(dct.items()):
            for f in self.formats:
                if str(f) == label:
                    dct["c%s" % target] = f
                    break
            else:
                raise AttributeError("Unknown format labeled %s." % (label,))
        return self.convert_fun(dct["csrc"], dct["cdst"])


class Matrix(object):
    """Simple matrix calculus.

    Examples
    --------

    >>> from python_utils.colour.future_colour import Matrix
    >>> Matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])([1, 2, 3])
    (1, 2, 3)

    >>> Matrix([[1, 0, 0], [0, 2, 0], [0, 0, 3]]) * [1, 1, 1]
    (1, 2, 3)

    """

    def __init__(self, m):
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        m : TYPE
            Description
        """
        self._m = m

    def __call__(self, v):
        """See :py:meth:`object.__call__`.

        Parameters
        ----------
        v : TYPE
            Description

        Returns
        -------
        TYPE
            Description
        """
        return tuple(sum(x1 * x2 for x1, x2 in zip(u, v)) for u in self._m)

    def __mul__(self, v):
        """See :py:meth:`object.__mul__`.

        Parameters
        ----------
        v : TYPE
            Description

        Returns
        -------
        TYPE
            Description
        """
        return self.__call__(v)


def register_converter(
    registry: ConverterRegistry, src: Any, dst: Any, **kwargs
) -> Callable[..., Callable[..., OutputColor3Tuple | OutputColor4Tuple]]:
    """Summary

    Parameters
    ----------
    registry : object
        Description
    src : object
        Description
    dst : object
        Description
    **kwargs
        Description

    Returns
    -------
    Callable[Callable[object, object], object]
        Description
    """

    def decorator(
        f: Callable[[InputColor3Tuple | InputColor4Tuple], OutputColor3Tuple | OutputColor4Tuple]
    ) -> Callable[[InputColor3Tuple | InputColor4Tuple], OutputColor3Tuple | OutputColor4Tuple]:
        """Summary

        Parameters
        ----------
        f : Callable[object, object]
            Description

        Returns
        -------
        Callable[object, object]
            Description
        """
        f.src = src  # type: ignore[attr-defined]
        f.dst = dst  # type: ignore[attr-defined]
        f.conv_kwargs = kwargs  # type: ignore[attr-defined]
        registry.append(f)
        return f

    return decorator


##
# Color Pickers
##


def RGB_color_picker(obj: Any) -> Color:
    """Build a color representation from the string representation of an object.

    This allows to quickly get a color from some data, with the
    additional benefit that the color will be the same as long as the
    (string representation of the) data is the same:

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

    >>> from python_utils.colour.future_colour import RGB_color_picker, Color

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


def mkDataSpace(
    formats: type[FormatRegistry],
    converters: type[ConverterRegistry],
    picker: Callable[[Any], int | str] = None,
    internal_format: object = None,
    input_formats: list = [],
    repr_format: object = None,
    string_format: object = None,
) -> object:
    """Returns a ``DataSpace`` provided a format registry and converters.

    Parameters
    ----------
    formats : type[FormatRegistry]
        Description
    converters : type[ConverterRegistry]
        Description
    picker : Callable[[object], Union[int, str]], optional
        Description
    internal_format : object, optional
        Description
    input_formats : list, optional
        Description
    repr_format : object, optional
        Description
    string_format : object, optional
        Description

    Returns
    -------
    object
        Description

    Raises
    ------
    ValueError
        Description

    Examples
    --------

    To create a data space you'll need a format registry, as this one:

    >>> from python_utils.colour.future_colour import FormatRegistry, register_format, mkDataSpace

    >>> fr = FormatRegistry()

    >>> @register_format(fr)
    ... class Dec(int, Format): pass
    >>> @register_format(fr)
    ... class Hex(String): pass
    >>> @register_format(fr)
    ... class Bin(String): pass

    To create a data space you'll need a converter registry, as this one:

    >>> from python_utils.colour.future_colour import ConverterRegistry, register_converter

    >>> cr = ConverterRegistry()

    >>> @register_converter(cr, Hex, Dec)
    ... def h2d(x): return int(x, 16)
    >>> @register_converter(cr, Dec, Hex)
    ... def d2h(x): return hex(x)
    >>> @register_converter(cr, Dec, Bin)
    ... def d2b(x): return bin(x)

    Then you can create the data space:

    >>> class Numeric(mkDataSpace(fr, cr)): pass

    **Instantiation**

    You can instantiate by explicitly giving the input format:

    >>> Numeric(dec=1)
    <Numeric 1>
    >>> Numeric(hex='0xc')
    <Numeric 12>

    Similarly, you can let the ``DataSpace`` object figure
    it out if you provide an already instantiated value:

    >>> Numeric(Dec(1))
    <Numeric 1>
    >>> Numeric(Hex('0xc'))
    <Numeric 12>

    And you can instantiate a ``DataSpace`` object with an other instance of
    it self:

    >>> Numeric(Numeric(1))
    <Numeric 1>

    You can also let the dataspace try to figure it out thanks to
    ``input_formats`` which is covered in the next section.

    And, finally, using the ``pick_for`` attribute, you can ask an
    automatic value for any type of python object. This value would
    then identify and should be always the same for the same object.
    This is covered in ``picker`` section.

    **input_formats**

    A dataspace can be instantiated with any type of object, in the
    case the object is not an instance of a format listed in the
    format registry, it'll have to try to try to instantiate one of
    these internal format with the value you have provided.  This is
    where the ``input_formats`` list will be used. Note that if it was
    not specified it will be the ``repr_format`` alone and if not
    specified, it'll fallback on the first available format alone in
    the format registry:

    >>> class Numeric(mkDataSpace(fr, cr)): pass
    >>> Numeric(1)
    <Numeric 1>

    But notice that hex value will be refused, as the only input format
    specified was (by default) the first one in the registry ``Dec``:

    >>> Numeric('0xc')
    Traceback (most recent call last):
    ...
    ValueError: No input formats are able to read '0xc' (tried Dec)

    So if you want, you can specify the list of input formats, they will be
    tried in the given order...

    >>> class Numeric(mkDataSpace(fr, cr, input_formats=[Dec, Hex])): pass
    >>> Numeric(1)
    <Numeric 1>
    >>> Numeric('0xc')
    <Numeric 12>

    Note also that if you don't want to specify ``input_formats``, using keyword
    can be allowed for one-time access:

    >>> class Numeric(mkDataSpace(fr, cr)): pass
    >>> Numeric(1)
    <Numeric 1>
    >>> Numeric(hex='0xc')
    <Numeric 12>

    **picker**

    By default, the picker mechanism is not operational:

    >>> class Numeric(mkDataSpace(fr, cr)): pass
    >>> Numeric(pick_for=object())
    Traceback (most recent call last):
    ...
    ValueError: Can't pick value as no picker was defined.

    You must define a ``picker``, a function that will output a value
    that could be instantiated by the ``DataSpace`` object:

    >>> class Numeric(mkDataSpace(fr, cr, picker=lambda x: 1)): pass
    >>> Numeric(pick_for=object())
    <Numeric 1>

    Of course, this is a dummy example, you should probably use
    ``hash`` or ``id`` or the string representation of your object to
    reliably give a different value to different object while having
    the same value for the same object.

    **Output formats**

    Dataspace will have mainly 2 output formats to follow python conventions:
    - a repr output
    - a string output
    These are manageable independently if needed.

    **object representation**

    There's a ``repr_format`` keyword to set the Python repr format, by
    default it will fallback to the first format available in the format
    registry:

    >>> class Numeric(mkDataSpace(fr, cr, repr_format=Hex)): pass
    >>> Numeric('0xc')
    <Numeric 0xc>

    Notice that the input format by default is the ``repr_format``. So:

    >>> class Numeric(mkDataSpace(fr, cr,
    ...     repr_format=Hex, input_formats=[Dec, ])): pass
    >>> Numeric(12)
    <Numeric 0xc>

    **object string output**

    There's a ``string_format`` keyword to set the Python string
    output used by ``%s`` or ``str()``, by default it will fallback to
    the ``repr_format`` value if defined and if not to the first
    format available in the format registry:

    >>> class Numeric(mkDataSpace(fr, cr, string_format=Hex)): pass
    >>> str(Numeric(12))
    '0xc'

    **Internal Format**

    ``DataSpace`` instance have an internal format which is the format
    that is effectively used to store the value. This format may be fixed
    of variable. By default it is variable, and this means that the value
    stored can change format any time.

    In some case you might want to use a fixed format to store your value.

    This will not change any visible behavior, the value being converted
    back and forth to the expected format anyway:

    >>> class Numeric(mkDataSpace(fr, cr, internal_format=Hex)): pass
    >>> Numeric(1)
    <Numeric 1>
    >>> Numeric(1).hex
    '0x1'

    In our example, we only have a path to convert from ``Dec`` to ``Bin`` and
    not the reverse:

    >>> class Numeric(mkDataSpace(fr, cr, internal_format=Bin)): pass
    >>> x = Numeric(15)
    >>> x.bin
    '0b1111'

    Instantiation, attribute access was okay, but:

    >>> x
    Traceback (most recent call last):
    ...
    ValueError: No conversion path found from bin to dec format.

    Because representation of the object should be in ``Dec`` format.

    **Attribute**

    There are 2 different type of magic attribute usable on
    ``DataSpace`` instances:
    - attributes that uses the format names and aims at setting
    or getting conversion in other formats.
    - attributes that uses subcomponent name of :py:class:`collections.namedtuple`

    **Format's name**

    Each ``DataSpace`` instance will provide attributes following the name
    of every format of the format registry that is reachable thanks to the
    converters.

    >>> class Numeric(mkDataSpace(fr, cr)): pass
    >>> Numeric(1).hex
    '0x1'
    >>> Numeric(1).bin
    '0b1'

    These attribute are read/write, so you can set the value of the instance
    easily:

    >>> x = Numeric(12)
    >>> x
    <Numeric 12>
    >>> x.hex = '0x12'
    >>> x
    <Numeric 18>
    >>> x.bin = '0b10101'

    We didn't provide any way to convert from binary to dec, which is
    the representation format here, so:

    >>> x
    Traceback (most recent call last):
    ...
    ValueError: No conversion path found from bin to dec format.

    Notice that this only makes an error upon usage, because the
    internal format (see section) is not fixed, and will thus follow
    blindly the last attribute assignation's format.

    **subcomponent attribute**

    This is a very special feature geared toward the usage of
    :py:class:`collections.namedtuple` formats.

    Most dataspace usage are used as reference systems translation
    between multi-dimensional data. Let's take for instance
    translation between polar coordinates and cartesian
    coordinates:

    >>> import math
    >>> fr2 = FormatRegistry()

    >>> @register_format(fr2)
    ... class Cartesian(Tuple("x", "y")): pass
    >>> @register_format(fr2)
    ... class Polar(Tuple("radius", "angle")): pass

    >>> cr2 = ConverterRegistry()

    >>> @register_converter(cr2, Cartesian, Polar)
    ... def c2p(v): return math.sqrt(v.x**2 + v.y**2), math.atan2(v.y, v.x)
    >>> @register_converter(cr2, Polar, Cartesian)
    ... def p2c(p):
    ...     return (p.radius * math.cos(p.angle),
    ...             p.radius * math.sin(p.angle))

    >>> class Point2D(mkDataSpace(fr2, cr2)): pass

    >>> point = Point2D((1, 0))
    >>> point
    <Point2D Cartesian(x=1, y=0)>

    The names of the subcomponent of the tuple are directly accessible
    (if there are no ambiguity):

    >>> point.x
    1

    >>> point.angle = math.pi
    >>> point.x
    -1.0

    In case of ambiguity, you can prefix your attribute label with the
    format names as such:

    >>> point.cartesian_y = 0.0
    >>> point.cartesian_x = 1.0
    >>> point.polar_angle
    0.0

    Here is such a case:

    >>> fr3 = FormatRegistry()

    >>> @register_format(fr3)
    ... class Normal(Tuple("x", "y")): pass
    >>> @register_format(fr3)
    ... class Inverted(Tuple("x", "y")): pass

    >>> cr3 = ConverterRegistry()

    >>> @register_converter(cr3, Normal, Inverted)
    ... def n2i(v): return v.y, v.x
    >>> @register_converter(cr3, Inverted, Normal)
    ... def i2n(v): return v.y, v.x

    In this case, we don't expect attribute ``x`` to be found:

    >>> class Point2D(mkDataSpace(fr3, cr3)): pass
    >>> Point2D((1, 2)).x = 2
    Traceback (most recent call last):
    ...
    ValueError: Ambiguous attribute 'x'. Try one of: normal_x, inverted_x

    >>> Point2D((1, 2)).x
    Traceback (most recent call last):
    ...
    ValueError: Ambiguous attribute 'x'. Try one of: normal_x, inverted_x

    **incorrect attribute**

    Of course, referring to an attribute label that can't be infered
    following the above rules then it'll cast an attribute error:

    >>> class Numeric(mkDataSpace(fr, cr)): pass
    >>> Numeric(1).foo
    Traceback (most recent call last):
    ...
    AttributeError: 'foo' not found

    You can't read it and can't set it:

    >>> Numeric(1).foo = 2
    Traceback (most recent call last):
    ...
    AttributeError: foo

    **Edge cases**

    If you provide an empty format registry, it'll complain:

    >>> mkDataSpace(FormatRegistry(), ConverterRegistry(), None)
    Traceback (most recent call last):
    ...
    ValueError: formats registry provided is empty.

    """

    if len(formats) == 0:
        raise ValueError("formats registry provided is empty.")

    # defaults
    repr_format = repr_format or formats[0]
    string_format = string_format or repr_format
    input_formats = input_formats or [repr_format]

    class DataSpace(object):
        """Relative Element in multi-representation data

        This object holds an internal representation of a data in a
        format (fixed or variable) and provide means to translate the
        data in available formats thanks to a set of converter functions.

        Attributes
        ----------
        equality : TYPE
            Description

        """

        _internal = None

        def __init__(
            self,
            value=None,
            pick_for=None,
            pick_key: Callable[[object], int | str] = hash_or_str,
            picker=None,
            **kwargs,
        ):
            """See :py:meth:`object.__init__`.

            Parameters
            ----------
            value : None, optional
                Description
            pick_for : None, optional
                Description
            pick_key : Callable[[object], Union[int, str]], optional
                Description
            picker : None, optional
                Description
            **kwargs
                Description

            Raises
            ------
            ValueError
                Description
            """
            if pick_key is None:

                def pick_key(x: object) -> object:
                    """Summary

                    Parameters
                    ----------
                    x : object
                        Description

                    Returns
                    -------
                    object
                        Description
                    """
                    return x

            if pick_for is not None:
                if not (picker or self._picker):
                    raise ValueError("Can't pick value as no picker was defined.")
                value = (picker or self._picker)(pick_key(pick_for))

            if isinstance(value, DataSpace):
                value_if_name = str(type(value._internal))
                setattr(self, value_if_name, getattr(value, value_if_name))
            elif isinstance(value, tuple(formats)):
                self._internal = (
                    value.convert(self._internal_format, converters)
                    if self._internal_format
                    else value
                )
            else:
                for f in input_formats:
                    try:
                        setattr(self, str(f), value)
                        break
                    except (ValueError, TypeError):
                        continue
                else:
                    # maybe keyword values were used
                    if len(set(kwargs.keys()) & set(str(f) for f in self._formats)) == 0:
                        raise ValueError(
                            "No input formats are able to read %r (tried %s)"
                            % (value, ", ".join(f.__name__ for f in input_formats))
                        )

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
            f, attr = self._formats.find(label)
            if f is not None:
                if attr is not None:
                    return getattr(getattr(self, str(f)), attr)
                return self._internal.convert(f, self._converters)
            raise AttributeError("'%s' not found" % label)

        def __setattr__(self, label, value):
            """See :py:meth:`object.__setattr__`.

            Parameters
            ----------
            label : TYPE
                Description
            value : TYPE
                Description

            Returns
            -------
            TYPE
                Description

            Raises
            ------
            AttributeError
                Description
            ValueError
                Description
            """
            if label.startswith("_") or label == "equality":
                self.__dict__[label] = value
                return

            f, attr = self._formats.find(label)
            if f is None:
                raise AttributeError(label)
            elif attr is None:
                if not isinstance(value, f):
                    try:
                        value = f(value)
                    except BaseException:
                        msg = format_last_exception()
                        raise ValueError(
                            "Instantiation of %s failed with given value %s."
                            "\n%s" % (type(value).__name__, value, msg)
                        )
                if self._internal_format:
                    value = value.convert(self._internal_format, self._converters)
                self._internal = value
            else:  # attr is not None
                setattr(self, str(f), getattr(self, str(f))._replace(**{attr: value}))

        def __str__(self):
            """See :py:meth:`object.__str__`.

            Returns
            -------
            TYPE
                Description
            """
            return "%s" % (getattr(self, str(self._string_format)),)

        def __repr__(self):
            """See :py:meth:`object.__repr__`.

            Returns
            -------
            TYPE
                Description
            """
            return "<%s %s>" % (
                self.__class__.__name__,
                getattr(self, str(self._repr_format)),
            )

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
            if isinstance(other, self.__class__):
                return self.equality(self, other)
            return NotImplemented

    frame = inspect.currentframe()
    argvalues = inspect.getargvalues(frame)
    for k in argvalues.args:
        value = argvalues.locals[k]
        if k == "picker" and value:
            value = staticmethod(value)
        setattr(DataSpace, "_%s" % k, value)
    return DataSpace


##
# Color equivalence
##


def RGB_equivalence(c1: type[Color], c2: type[Color]) -> bool:
    """Summary

    Parameters
    ----------
    c1 : type[Color]
        Description
    c2 : type[Color]
        Description

    Returns
    -------
    bool
        Description
    """
    return c1.hex == c2.hex


def HSL_equivalence(c1: type[Color], c2: type[Color]) -> bool:
    """Summary

    Parameters
    ----------
    c1 : type[Color]
        Description
    c2 : type[Color]
        Description

    Returns
    -------
    bool
        Description
    """
    return c1.hsl == c2.hsl


##
# Module wide color object
##


def make_color_factory(**kwargs_defaults) -> object:
    """Summary

    Parameters
    ----------
    **kwargs_defaults
        Description

    Returns
    -------
    object
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


##
# Color Formats
##

Formats: FormatRegistry = FormatRegistry()


@register_format(Formats)
class X11(String):
    """Summary

    Attributes
    ----------
    default : str
        Description
    """

    default = "blue"

    @classmethod
    def _validate(cls, s):
        """Summary

        Parameters
        ----------
        s : TYPE
            Description

        Returns
        -------
        TYPE
            Description

        Raises
        ------
        ValueError
            Description
        """
        if s.startswith("#"):
            if not HexS.regex.match(s):
                raise ValueError("Invalid hex string specifier '%s' for X11 format" % s)
            return hex2x11(s)

        x11 = sanitize_color_name(s)

        if x11 not in X11_COLOR_NAME_TO_RGB:
            raise ValueError("%r is not a recognized color for X11 format." % x11)

        return x11


@register_format(Formats)
class Web(String):
    """String object with English color names or use short or long hex representation.

    This format is used most notably in HTML/CSS for its ease of use. ex: 'red',
    '#123456', '#fff' are all web representation.

    Attributes
    ----------
    default : str
        Description

    Examples
    --------

    >>> from python_utils.colour.future_colour import Web

    >>> Web('white')
    'white'
    >>> Web.white
    'white'

    >>> Web('foo')
    Traceback (most recent call last):
    ...
    ValueError: 'foo' is not a recognized color for Web format.

    >>> Web('#foo')
    Traceback (most recent call last):
    ...
    ValueError: Invalid hex string specifier '#foo' for Web format

    Web has a default value to 'blue':

    >>> Web(None)
    'blue'

    """

    default = "blue"

    @classmethod
    def _validate(cls, s):
        """Summary

        Parameters
        ----------
        s : TYPE
            Description

        Returns
        -------
        TYPE
            Description

        Raises
        ------
        ValueError
            Description
        """
        if s.startswith("#"):
            if not HexS.regex.match(s):
                raise ValueError("Invalid hex string specifier '%s' for Web format" % s)
            return hex2web(s)

        web = sanitize_color_name(s)

        if web not in WEB_COLOR_NAME_TO_RGB:
            raise ValueError("%r is not a recognized color for Web format." % web)

        return web


@register_format(Formats)
class HSL(Tuple("hue", "saturation", "luminance")):
    """3-tuple of Hue, Saturation, Lightness all between 0.0 and 1.0

    Examples
    --------

    As all ``Format`` subclass, it can instantiate color based on the X11 color names:

    >>> from python_utils.colour.future_colour import HSL

    >>> HSL.white
    HSL(hue=0.0, saturation=0.0, luminance=1.0)

    """


@register_format(Formats)
class HSV(Tuple("hue", "saturation", "value")):
    """3-tuple of Hue, Saturation, Value all between 0.0 and 1.0

    Examples
    --------

    As all ``Format`` subclass, it can instantiate color based on the X11 color names:

    >>> from python_utils.colour.future_colour import HSV

    >>> HSV.blue
    HSV(hue=0.66..., saturation=1.0, value=1.0)

    """


@register_format(Formats)
class RGB(Tuple("red", "green", "blue")):
    """3-tuple of Red, Green, Blue all values between 0.0 and 1.0

    Examples
    --------

    As all ``Format`` subclass, it can instantiate color based on the X11 color names:

    >>> from python_utils.colour.future_colour import RGB

    >>> RGB.darkcyan
    RGB(red=0.0, green=0.545..., blue=0.545...)
    >>> RGB.WHITE
    RGB(red=1.0, green=1.0, blue=1.0)
    >>> RGB.BLUE
    RGB(red=0.0, green=0.0, blue=1.0)

    >>> RGB.DOESNOTEXIST
    Traceback (most recent call last):
    ...
    AttributeError: ... has no attribute 'DOESNOTEXIST'

    """


@register_format(Formats)
class YIQ(Tuple("luma", "inphase", "quadrature")):
    """3-tuple of ``luma``, ``inphase``, ``quadrature``.

    Examples
    --------

    As all ``Format`` subclass, it can instantiate color based on the X11 color names:

    >>> from python_utils.colour.future_colour import YIQ

    >>> YIQ.green
    YIQ(luma=0.296156862745098, inphase=-0.13919372549019604, quadrature=-0.2635796078431372)

    """


@register_format(Formats)
class CMY(Tuple("cyan", "magenta", "yellow")):
    """3-tuple of ``cyan``, ``magenta``, and ``yellow``, all values are between 0. and 1.

    Examples
    --------

    As all ``Format`` subclass, it can instantiate color based on the X11 color names:

    >>> from python_utils.colour.future_colour import CMY

    >>> CMY.CYAN  ## Avoid using 'cyan' as it conflict with property
    CMY(cyan=1.0, magenta=0.0, yellow=0.0)

    """


@register_format(Formats)
class CMYK(Tuple("cyan", "magenta", "yellow", "key")):
    """4-tuple of ``cyan``, ``magenta``, ``yellow``, and ``key`` all values are between 0 and 1.

    Examples
    --------

    As all ``Format`` subclass, it can instantiate color based on the X11
    color names:

    >>> from python_utils.colour.future_colour import CMYK

    >>> CMYK.CYAN  ## Avoid using 'cyan' as it conflict with property
    CMYK(cyan=1.0, magenta=0.0, yellow=0.0, key=0.0)
    >>> CMYK.black
    CMYK(cyan=0.0, magenta=0.0, yellow=0.0, key=1.0)

    """


@register_format(Formats)
class YUV(Tuple("luma", "u", "v")):
    """3-tuple of ``luma``, ``u``, ``v``.

    ``luma`` is between 0.0 and 1.0, ``u`` and ``v`` are coordinates with values between -1.0 and 1.0.

    Examples
    --------

    >>> from python_utils.colour.future_colour import YUV

    >>> YUV.blue
    YUV(luma=0.114, u=0.436, v=-0.10001)

    """


@register_format(Formats)
class Hex(String):
    """7-chars string starting with '#' and with ``red``, ``green``, ``blue`` values.

    Each color is expressed in 2 hex digit each.

    Attributes
    ----------
    regex : re.Pattern
        Description

    Note
    ----
    This format accept only 6-hex digit (``#ffffff``).

    Examples
    --------

    As all ``Format`` subclass, it can instantiate color based on the X11 color names:

    >>> from python_utils.colour.future_colour import Hex

    >>> Hex.WHITE
    '#ffffff'
    >>> type(Hex.WHITE)
    <Format Hex>
    >>> Hex.BLUE
    '#0000ff'

    """

    regex = LONG_HEX_COLOR


@register_format(Formats)
class HexS(String):
    """string starting with '#' and with red, green, blue values

    This format accept color in 3 or 6 value ex: ``#fff`` or ``#ffffff``

    Attributes
    ----------
    regex : re.Pattern
        Description

    """

    regex = SHORT_OR_LONG_HEX_COLOR


##
# Converters
##


# Module wide converters
Converters: ConverterRegistry = ConverterRegistry()


@register_converter(Converters, HSL, RGB)
def hsl2rgb(hsl: InputColor3Tuple) -> OutputColor3Tuple:
    """Convert `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__ representation
    towards `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__.

    Hue, Saturation, Range from Lightness is a float between 0 and 1

    This algorithm came from `EasyRGB <http://www.easyrgb.com/index.php?X=MATH&H=19#text19>`__.

    Note that Hue can be set to any value but as it is a rotation
    around the chromatic circle, any value above 1 or below 0 can be
    expressed by a value between 0 and 1 (Note that h=0 is equiv to
    h=1).

    Parameters
    ----------
    hsl : InputColor3Tuple
        3-tuple with Hue, position around the chromatic circle (h=1 equiv h=0)
        Saturation, color saturation (0=full gray, 1=full color)
        Lightness, Overhaul lightness (0=full black, 1=full white)

    Returns
    -------
    OutputColor3Tuple
        3-tuple for `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ values in float between 0 and 1.

    Raises
    ------
    ValueError
        Description

    Examples
    --------

    Here are some quick notion of `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__
    to `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ conversions.

    >>> from python_utils.colour.future_colour import hsl2rgb

    With a lightness put at 0, `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ is always rgbblack

    >>> hsl2rgb((0.0, 0.0, 0.0))
    (0.0, 0.0, 0.0)
    >>> hsl2rgb((0.5, 0.0, 0.0))
    (0.0, 0.0, 0.0)
    >>> hsl2rgb((0.5, 0.5, 0.0))
    (0.0, 0.0, 0.0)

    Same for lightness put at 1, `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ is always rgbwhite

    >>> hsl2rgb((0.0, 0.0, 1.0))
    (1.0, 1.0, 1.0)
    >>> hsl2rgb((0.5, 0.0, 1.0))
    (1.0, 1.0, 1.0)
    >>> hsl2rgb((0.5, 0.5, 1.0))
    (1.0, 1.0, 1.0)

    With saturation put at 0, the `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ should be equal to Lightness:

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
    h, s, l = [float(v) for v in hsl]  # noqa: E741

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


@register_converter(Converters, RGB, HSL)
def rgb2hsl(rgb: InputColor3Tuple) -> OutputColor3Tuple:
    """Convert `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ representation towards
    `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__.

    This algorithm came from `EasyRGB <http://www.easyrgb.com/index.php?X=MATH&H=19#text19>`__.

    Parameters
    ----------
    rgb : InputColor3Tuple
        rgb: 3-tuple Red, Green, Blue amount (floats between 0 and 1)

    Returns
    -------
    OutputColor3Tuple
        3-tuple for `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__ values in float between 0 and 1.

    Raises
    ------
    ValueError
        Description

    Examples
    --------

    Here are some quick notion of `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ to
    `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__ conversions.

    >>> from python_utils.colour.future_colour import rgb2hsl

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

    l = vsum / 2

    if diff < FLOAT_ERROR:  # This is a gray, no chroma...
        return 0.0, 0.0, l

    ##
    # Chromatic data...
    ##

    # Saturation
    if l < 0.5:
        s = diff / vsum
    else:
        s = diff / (2.0 - vsum)
    dr, dg, db = tuple((vmax - x) / diff for x in (r, g, b))

    h = db - dg if r == vmax else 2.0 + dr - db if g == vmax else 4.0 + dg - dr

    h /= 6

    while h < 0:
        h += 1
    while h > 1:
        h -= 1

    return h, s, l


@register_converter(Converters, Hex, HexS)
def hex2hexs(hex: str) -> str:
    """Shorten from 6 to 3 hex representation if possible

    Parameters
    ----------
    hex : str
        Description

    Returns
    -------
    str
        Description

    Examples
    --------

    >>> from python_utils.colour.future_colour import hex2hexs

    Provided a long string hex format, it should shorten it when
    possible:

    >>> hex2hexs('#00ff00')
    '#0f0'

    In the following case, it is not possible to shorten, thus:

    >>> hex2hexs('#01ff00')
    '#01ff00'

    """

    if len(hex) == 7 and hex[1::2] == hex[2::2]:
        return "#" + "".join(hex[1::2])
    return hex


@register_converter(Converters, HexS, Hex)
def hexs2hex(hex: str) -> str:
    """Enlarge possible short 3 hex char string to give full hex 6 char string

    Parameters
    ----------
    hex : str
        Description

    Returns
    -------
    str
        Description

    Examples
    --------

    >>> from python_utils.colour.future_colour import hexs2hex

    Provided a short string hex format, it should enlarge it:

    >>> hexs2hex('#0f0')
    '#00ff00'

    In the following case, it is already enlargened, thus:

    >>> hexs2hex('#01ff00')
    '#01ff00'

    """
    if not Hex.regex.match(hex):
        return "#" + "".join([("%s" % (t,)) * 2 for t in hex[1:]])
    return hex


@register_converter(Converters, RGB, Hex)
def rgb2hex(rgb: InputColor3Tuple) -> str:
    """Transform `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ tuple to hex `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ representation

    Parameters
    ----------
    rgb : InputColor3Tuple
        `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ 3-tuple of float between 0 and 1

    Returns
    -------
    str
        3 hex char or 6 hex char string representation with '#' prefix

    Examples
    --------

    >>> from python_utils.colour.future_colour import rgb2hex

    >>> rgb2hex((0.0, 1.0, 0.0))
    '#00ff00'

    Rounding try to be as natural as possible:

    >>> rgb2hex((0.0, 0.999999, 1.0))
    '#00ffff'

    >>> rgb2hex((0.5, 0.999999, 1.0))
    '#7fffff'

    """

    return "#" + "".join(["%02x" % int(float(c) * 255 + 0.5 - FLOAT_ERROR) for c in rgb])


@register_converter(Converters, Hex, RGB)
def hex2rgb(hex: str) -> OutputColor3Tuple:
    """Transform hex `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ representation to `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ tuple

    Parameters
    ----------
    hex : str
        3 hex char or 6 hex char string representation with '#' prefix.

    Returns
    -------
    OutputColor3Tuple
        `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ 3-tuple of float between 0 and 1

    Raises
    ------
    ValueError
        Description

    Examples
    --------

    >>> from python_utils.colour.future_colour import hex2rgb

    >>> hex2rgb('#00ff00')
    (0.0, 1.0, 0.0)

    >>> hex2rgb('#0f0')
    (0.0, 1.0, 0.0)

    >>> hex2rgb('#aaa')
    (0.66..., 0.66..., 0.66...)

    >>> hex2rgb('#aa')
    Traceback (most recent call last):
    ...
    ValueError: Invalid value '#aa' provided as hex color for rgb conversion.

    """

    try:
        hex = hex[1:]

        if len(hex) == 6:
            r, g, b = hex[0:2], hex[2:4], hex[4:6]
        elif len(hex) == 3:
            r, g, b = hex[0] * 2, hex[1] * 2, hex[2] * 2
        else:
            raise ValueError()
    except BaseException:
        raise ValueError("Invalid value %r provided as HEX color for RGB conversion." % hex)

    return tuple(float(int(v, 16)) / 255 for v in (r, g, b))


@register_converter(Converters, Hex, Web)
def hex2web(hex: str) -> str:
    """Converts Hex representation to Web

    Web representation uses X11 rgb.txt to define conversion
    between `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ and English color names.

    Parameters
    ----------
    hex : str
        3 hex char or 6 hex char string representation

    Returns
    -------
    str
        web string representation (human readable if possible)

    Examples
    --------

    >>> from python_utils.colour.future_colour import hex2web

    >>> hex2web('#ff0000')
    'red'

    >>> hex2web('#aaaaaa')
    '#aaa'

    >>> hex2web('#acacac')
    '#acacac'

    """
    dec_rgb = tuple(int(v * 255) for v in hex2rgb(hex))
    if dec_rgb in RGB_TO_WEB_COLOR_NAMES:
        # Take all names assigned to the color.
        return RGB_TO_WEB_COLOR_NAMES[dec_rgb][0]

    return hex2hexs(hex)


@register_converter(Converters, Web, Hex)
def web2hex(web: str) -> str:
    """Converts Web representation to Hex

    Web representation uses X11 rgb.txt (converted in array in this file)
    to define conversion between `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ and English color names.

    As of https://www.w3.org/TR/css3-color/#svg-color, there are 147 names
    recognized.

    Parameters
    ----------
    web : str
        web string representation (human readable if possible)

    Returns
    -------
    str
        3 hex char or 6 hex char string representation

    Raises
    ------
    AttributeError
        Description
    ValueError
        Description

    Examples
    --------

    >>> from python_utils.colour.future_colour import web2hex

    >>> web2hex('red')
    '#ff0000'

    >>> web2hex('#aaa')
    '#aaaaaa'

    >>> web2hex('#foo')
    Traceback (most recent call last):
    ...
    AttributeError: '#foo' is not in web format. Need 3 or 6 hex digit.

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

    And color names are case insensitive:

    >>> from python_utils.colour.future_colour import Color
    >>> Color('RED')
    <Color red>

    """
    if web.startswith("#"):
        if Hex.regex.match(web):
            return web.lower()
        elif HexS.regex.match(web):
            return hexs2hex(web)
        raise AttributeError("%r is not in web format. Need 3 or 6 hex digit." % web)

    web = sanitize_color_name(web)
    if web not in WEB_COLOR_NAME_TO_RGB:
        raise ValueError("%r is not a recognized color." % web)

    return rgb2hex([float(int(v)) / 255 for v in WEB_COLOR_NAME_TO_RGB[web]])


@register_converter(Converters, Hex, X11)
def hex2x11(hex: str) -> str:
    """Summary

    Parameters
    ----------
    hex : str
        Description

    Returns
    -------
    str
        Description
    """
    dec_rgb = tuple(int(v * 255) for v in hex2rgb(hex))
    if dec_rgb in RGB_TO_X11_COLOR_NAMES:
        return RGB_TO_X11_COLOR_NAMES[dec_rgb][0]

    return hex2hexs(hex)


@register_converter(Converters, X11, Hex)
def x112hex(x11: str) -> str:
    """Summary

    Parameters
    ----------
    x11 : str
        Description

    Returns
    -------
    str
        Description

    Raises
    ------
    AttributeError
        Description
    ValueError
        Description
    """
    if x11.startswith("#"):
        if Hex.regex.match(x11):
            return x11.lower()
        elif HexS.regex.match(x11):
            return hexs2hex(x11)
        raise AttributeError("%r is not in X11 format. Need 3 or 6 hex digit." % x11)

    x11 = sanitize_color_name(x11)
    if x11 not in X11_COLOR_NAME_TO_RGB:
        raise ValueError("%r is not a recognized color." % x11)

    return rgb2hex([float(int(v)) / 255 for v in X11_COLOR_NAME_TO_RGB[x11]])


register_converter(Converters, RGB, HSV)(lambda rgb: colorsys.rgb_to_hsv(*rgb))
register_converter(Converters, HSV, RGB)(lambda hsv: colorsys.hsv_to_rgb(*hsv))
register_converter(Converters, RGB, YIQ)(lambda rgb: colorsys.rgb_to_yiq(*rgb))
register_converter(Converters, YIQ, RGB)(lambda yiq: colorsys.yiq_to_rgb(*yiq))
# FIXME: Something is rotten... This can't possibly be right. Neither of the two.
register_converter(Converters, RGB, CMY)(lambda rgb: tuple(1 - u for u in rgb))
register_converter(Converters, CMY, RGB)(lambda rgb: tuple(1 - u for u in rgb))


@register_converter(Converters, CMY, CMYK)
def cmy2cmyk(cmy: InputColor3Tuple) -> OutputColor4Tuple:
    """Converts `CMY <https://en.wikipedia.org/wiki/CMY_color_model>`__ representation
    to `CMYK <https://en.wikipedia.org/wiki/CMYK_color_model>`__.

    Parameters
    ----------
    cmy : InputColor3Tuple
        3-tuple with cyan, magenta, yellow values

    Returns
    -------
    OutputColor4Tuple
        4-tuple with cyan, magenta, yellow, key values

    Raises
    ------
    ValueError
        Description

    Examples
    --------

    >>> from python_utils.colour.future_colour import cmy2cmyk

    >>> cmy2cmyk((0, 0, 0))
    (0.0, 0.0, 0.0, 0.0)

    >>> cmy2cmyk((1, 1, 1))
    (0.0, 0.0, 0.0, 1.0)

    >>> cmy2cmyk((0.5, 0.6, 0.7))
    (0.0, 0.19..., 0.39..., 0.5)

    >>> cmy2cmyk((2, 0, 0))
    Traceback (most recent call last):
    ...
    ValueError: Cyan must be between 0 and 1. You provided 2.0.

    """
    c, m, y = [float(v) for v in cmy]

    for name, v in {"Cyan": c, "Magenta": m, "Yellow": y}.items():
        if not (0 - FLOAT_ERROR <= v <= 1 + FLOAT_ERROR):
            raise ValueError("%s must be between 0 and 1. You provided %r." % (name, v))
    k = min(c, m, y)
    if k > 1 - FLOAT_ERROR:
        return 0.0, 0.0, 0.0, k

    inv = float(1 - k)

    return tuple(((x - k) / inv) for x in cmy) + (k,)


@register_converter(Converters, CMYK, CMY)
def cmyk2cmy(cmyk: InputColor4Tuple) -> OutputColor3Tuple:
    """Converts `CMY <https://en.wikipedia.org/wiki/CMY_color_model>`__ representation
    to `CMYK <https://en.wikipedia.org/wiki/CMYK_color_model>`__.

    Parameters
    ----------
    cmyk : InputColor4Tuple
        4-tuple with cyan, magenta, yellow, key values.

    Returns
    -------
    OutputColor3Tuple
        3-tuple with cyan, magenta, yellow values.

    Raises
    ------
    ValueError
        Description

    Examples
    --------

    >>> from python_utils.colour.future_colour import cmyk2cmy

    >>> cmyk2cmy((0, 0, 0, 0))
    (0.0, 0.0, 0.0)

    >>> cmyk2cmy((0, 0, 0, 1))
    (1.0, 1.0, 1.0)

    >>> cmyk2cmy((2.0, 0, 0, 0))
    Traceback (most recent call last):
    ...
    ValueError: Cyan must be between 0 and 1. You provided 2.0.

    """
    c, m, y, k = [float(v) for v in cmyk]
    for name, v in {"Cyan": c, "Magenta": m, "Yellow": y, "Key": k}.items():
        if not (0 - FLOAT_ERROR <= v <= 1 + FLOAT_ERROR):
            raise ValueError("%s must be between 0 and 1. You provided %r." % (name, v))
    return tuple((x * (1 - k)) + k for x in (c, m, y))


RGB_TO_YUV: type[Matrix] = Matrix(
    [
        [0.299, 0.587, 0.114],
        [-0.14713, -0.28886, 0.436],
        [0.615, -0.51499, -0.10001],
    ]
)


@register_converter(Converters, RGB, YUV)
def rgb2yuv(rgb: RestrictedInputColor3Tuple) -> OutputColor3Tuple:
    """Converting from `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ to
    `YUV <https://en.wikipedia.org/wiki/YUV>`__ using BT.709 conversion.

    Parameters
    ----------
    rgb : RestrictedInputColor3Tuple
        Description

    Returns
    -------
    OutputColor3Tuple
        Description

    Examples
    --------

    >>> from python_utils.colour.future_colour import rgb2yuv

    >>> rgb2yuv((1., 0., 0.))
    (0.299, -0.14713, 0.615)

    """
    return RGB_TO_YUV(rgb)


# Use:
##
# >>> import colour
# >>> from numpy import matrix, linalg
# >>> print (linalg.inv(RGB_TO_YUV))
##
# To get the reverse matrix.
YUV_TO_RGB: type[Matrix] = Matrix(
    [
        [1.0, -0.0000117983844, 1.13983458],
        [1.00000395, -0.394646053, -0.580594234],
        [0.999979679, 2.03211194, -0.0000151129807],
    ]
)


@register_converter(Converters, YUV, RGB)
def yuv2rgb(yuv: RestrictedInputColor3Tuple) -> OutputColor3Tuple:
    """Converting from `YUV <https://en.wikipedia.org/wiki/YUV>`__
    to `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ using BT.709 conversion.

    Parameters
    ----------
    yuv : RestrictedInputColor3Tuple
        Description

    Returns
    -------
    OutputColor3Tuple
        Description

    Examples
    --------

    >>> from python_utils.colour.future_colour import yuv2rgb

    >>> yuv2rgb((1., 0., 0.))
    (1.0, 1.0..., 0.99...)

    """

    return YUV_TO_RGB(yuv)


class Color(mkDataSpace(formats=Formats, converters=Converters, picker=RGB_color_picker)):
    """Abstraction of a color object.

    Color object keeps information of a color. It can input/output to
    different formats (the ones registered in Formats object) and
    their partial representation.

    Examples
    --------

    >>> from python_utils.colour.future_colour import Color, HSL

    >>> b = Color()
    >>> b.hsl = HSL.BLUE

    **Access values**

    Direct attribute will be resolved in available format

    >>> b.red
    0.0
    >>> b.blue
    1.0
    >>> b.green
    0.0

    In the previous example, attributes are resolved as names of component of the
    `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ format. In some case you need to be more
    specific by prefixing by the format name, so:

    >>> b.red == b.rgb_red
    True

    `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__ components for instances are accessible

    >>> b.hsl_saturation
    1.0
    >>> b.hsl_hue
    0.66...
    >>> b.hsl_luminance
    0.5

    >>> b.rgb
    RGB(red=0.0, green=0.0, blue=1.0)
    >>> b.hsl
    HSL(hue=0.66..., saturation=1.0, luminance=0.5)
    >>> b.hsv
    HSV(hue=0.66..., saturation=1.0, value=1.0)
    >>> b.yiq
    YIQ(luma=0.11, inphase=-0.32..., quadrature=0.31...)
    >>> b.hex
    '#0000ff'
    >>> b.web
    'blue'
    >>> b.yuv
    YUV(luma=0.114, u=0.436, v=-0.10001)

    **Change values**

    Let's change Hue toward red tint:

    >>> b.hsl_hue = 0.0
    >>> b.hex
    '#ff0000'

    >>> b.hsl_hue = 2.0/3
    >>> b.hex
    '#0000ff'

    In the other way round

    >>> b.hexs = '#f00'
    >>> b.hsl
    HSL(hue=0.0, saturation=1.0, luminance=0.5)

    Long hex can be accessed directly

    >>> b.hex = '#123456'
    >>> b.hex
    '#123456'
    >>> b.hexs
    '#123456'

    >>> b.hex = '#ff0000'
    >>> b.hex
    '#ff0000'
    >>> b.hexs
    '#f00'

    **Convenience**

    >>> c = Color('blue')
    >>> c
    <Color blue>
    >>> c.hsl_hue = 0
    >>> c
    <Color red>

    >>> c.hsl_saturation = 0.0
    >>> c.hsl
    HSL(hue=..., saturation=0.0, luminance=0.5)
    >>> c.rgb
    RGB(red=0.5, green=0.5, blue=0.5)
    >>> c.hex
    '#7f7f7f'
    >>> c
    <Color gray50>

    >>> c.luminance = 0.0
    >>> c
    <Color black>

    >>> c.hex
    '#000000'

    >>> c.green = 1.0
    >>> c.blue = 1.0
    >>> c.hex
    '#00ffff'
    >>> c
    <Color aqua>

    Equivalently, in one go:

    >>> c.rgb = (1, 1, 0)
    >>> c
    <Color yellow>

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

    `HSV <https://en.wikipedia.org/wiki/HSL_and_HSV>`__ Support

    >>> c = Color('red')
    >>> c.hsv
    HSV(hue=0.0, saturation=1.0, value=1.0)
    >>> c.value
    1.0

    >>> c.rgb = (0.099, 0.795, 0.591)
    >>> c.hsv
    HSV(hue=0.45..., saturation=0.87..., value=0.79...)
    >>> c.hsv = HSV(hue=0.0, saturation=0.5, value=1.0)
    >>> c.hex
    '#ff7f7f'

    Notice how `HSV <https://en.wikipedia.org/wiki/HSL_and_HSV>`__ saturation
    is different from `HSL <https://en.wikipedia.org/wiki/HSL_and_HSV>`__ one

    >>> c.hsv_saturation
    0.5
    >>> c.hsl_saturation
    1.0

    `YIQ Support <https://en.wikipedia.org/wiki/YIQ>`__

    >>> c = Color('green')
    >>> c.yiq
    YIQ(luma=0.59, inphase=-0.2773, quadrature=-0.5250999999999999)
    >>> c.yiq_luma
    0.59

    Reversing a https://en.wikipedia.org/wiki/YIQ value to
    `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__

    >>> c = Color(c.yiq)
    >>> c.hex
    '#00ff00'

    `CMY <https://en.wikipedia.org/wiki/CMY_color_model>`__/
    `CMYK <https://en.wikipedia.org/wiki/CMYK_color_model>`__ Support

    >>> c = Color('green')
    >>> c.cmyk
    CMYK(cyan=1.0, magenta=0.0, yellow=1.0, key=0.0)
    >>> c.key
    0.0

    Reversing a `CMYK <https://en.wikipedia.org/wiki/CMYK_color_model>`__ value to
    `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__

    >>> c = Color(c.cmyk)
    >>> c.hex
    '#00ff00'

    **Recursive initialization**

    To support blind conversion of web strings (or already converted object),
    the Color object supports instantiation with another Color object.

    >>> Color(Color(Color('red')))
    <Color red>

    **Equality support**

    Default equality is `RGB <https://en.wikipedia.org/wiki/RGB_color_model>`__ hex comparison

    >>> Color('red') == Color('blue')
    False
    >>> Color('red') == Color('red')
    True
    >>> Color('red') != Color('blue')
    True
    >>> Color('red') != Color('red')
    False

    But this can be changed

    >>> saturation_equality = lambda c1, c2: c1.luminance == c2.luminance
    >>> Color('red', equality=saturation_equality) == Color('blue')
    True

    **Sub-classing support**

    You should be able to subclass ``Color`` object without any issues:

    >>> class Tint(Color):
    ...     pass

    And keep the internal API working

    >>> Tint("red").hsl
    HSL(hue=0.0, saturation=1.0, luminance=0.5)

    """

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
        for hsl in color_scale(self.hsl, self.__class__(value).hsl, steps - 1):
            yield self.__class__(hsl=hsl)


class Colour(Color):
    """Class equivalent to :py:class:`Color` class to add consistency with the name of the module.

    >>> from python_utils.colour.future_colour import Colour, Color

    >>> red = Colour("red")
    >>> isinstance(red, Color)
    True
    """
