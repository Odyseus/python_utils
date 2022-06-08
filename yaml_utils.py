# -*- coding: utf-8 -*-
"""YAML utils.

Note
----
I created the ordered load/dump methods because the default sorting capabilities suck (the "a" and "A"
characters are in the EXACT SAME PLACE ALPHABETICALLY). So, I sort my data my way before dumping
it to a YAML document.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any
    from typing import IO

from collections import OrderedDict

from . import yaml


def load(stream: str | bytes | IO, **kwargs) -> Any:
    """Parse the first YAML document in a stream and produce the corresponding Python object.

    Parameters
    ----------
    stream : str | bytes | IO
        The YAML data to parse into a Python object. It could be a string,
        bytes or a file object.
    **kwargs
        Extra keyword arguments to pass to ``yaml.load``.

    Returns
    -------
    Any
        A Python object.
    """
    return yaml.load(stream, Loader=yaml.SafeLoader, **kwargs)


def dump(data: Any, stream: IO | None = None, **kwargs) -> str | bytes | None:
    """Serialize a Python object into a YAML stream.

    Parameters
    ----------
    data : Any
        Data to dump.
    stream : IO | None, optional
        A file object to dump the YAML data into.
    **kwargs
        Extra keyword arguments to pass to ``yaml.dump``.

    Returns
    -------
    str | bytes | None
        The serialized data if ``stream`` is ``None``.
    """
    return yaml.dump(data, stream, Dumper=yaml.SafeDumper, **kwargs)


class OrderedLoader(yaml.SafeLoader):
    """Ordered YAML loader."""

    pass


def _construct_mapping(loader: yaml.Loader, node: yaml.nodes.Node):
    """Construct mapping.

    Parameters
    ----------
    loader : yaml.Loader
        A ``yaml.Loader`` instance.
    node : yaml.nodes.Node
        A ``Node`` object.

    Returns
    -------
    OrderedDict
        Produced corresponding Python object.
    """
    loader.flatten_mapping(node)
    return OrderedDict(loader.construct_pairs(node))


OrderedLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


class OrderedDumper(yaml.SafeDumper):
    """Ordered YAML dumper."""

    pass


def _dict_representer(dumper: yaml.Dumper, data: OrderedDict):
    """Dict representer.

    Parameters
    ----------
    dumper : yaml.Dumper
        A ``yaml.Dumper`` instance.
    data : OrderedDict
        An ``OrderedDict`` instance.

    Returns
    -------
    yaml.nodes.Node
        Produced representation node.
    """
    return dumper.represent_mapping(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, data.items())


OrderedDumper.add_representer(OrderedDict, _dict_representer)


def ordered_load(stream: str | bytes | IO, **kwargs) -> Any:
    """Same as :any:`yaml_utils.load`.

    Parameters
    ----------
    stream : str | bytes | IO
        The YAML data to parse into a Python object. It could be a string,
        bytes or a file object.
    **kwargs
        Extra keyword arguments to pass to ``yaml.load``.

    Returns
    -------
    Any
        A Python object.
    """
    return yaml.load(stream, Loader=OrderedLoader, **kwargs)


def ordered_dump(data: OrderedDict, stream: IO | None = None, **kwargs) -> str | bytes | None:
    """Same as :any:`yaml_utils.dump`.

    Parameters
    ----------
    data : OrderedDict
        An ``OrderedDict`` instance.
    stream : IO | None, optional
        A file object to dump the YAML data into.
    **kwargs
        Extra keyword arguments to pass to ``yaml.dump``.

    Returns
    -------
    str | bytes | None
        The serialized data if ``stream`` is ``None``.

    Examples
    --------
    >>> from python_utils import yaml_utils
    >>> from collections import OrderedDict
    >>> obj = {
    ...     "a": "",
    ...     "b": "",
    ...     "c": "",
    ...     "d": "",
    ...     "A": "",
    ...     "B": "",
    ...     "C": "",
    ...     "D": "",
    ... }
    >>> print(yaml_utils.dump(obj))
    A: ''
    B: ''
    C: ''
    D: ''
    a: ''
    b: ''
    c: ''
    d: ''
    <BLANKLINE>

    >>> obj_sorted = OrderedDict(sorted(obj.items(), key=lambda k: k[0].casefold()))
    >>> print(yaml_utils.ordered_dump(obj_sorted))
    a: ''
    A: ''
    b: ''
    B: ''
    c: ''
    C: ''
    d: ''
    D: ''
    <BLANKLINE>

    """
    return yaml.dump(data, stream=stream, Dumper=OrderedDumper, **kwargs)


if __name__ == "__main__":
    pass
