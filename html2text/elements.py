# -*- coding: utf-8 -*-
"""Summary
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Optional


class AnchorElement:
    """Anchor element.

    Attributes
    ----------
    attrs : dict[str, Optional[str]]
        Description
    count : int
        Description
    outcount : int
        Description
    """

    __slots__ = ["attrs", "count", "outcount"]

    def __init__(self, attrs: dict[str, Optional[str]], count: int, outcount: int):
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        attrs : dict[str, Optional[str]]
            Description
        count : int
            Description
        outcount : int
            Description
        """
        self.attrs: dict[str, Optional[str]] = attrs
        self.count: int = count
        self.outcount: int = outcount


class ListElement:
    """List element.

    Attributes
    ----------
    name : str
        Description
    num : int
        Description
    """

    __slots__ = ["name", "num"]

    def __init__(self, name: str, num: int):
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        name : str
            Description
        num : int
            Description
        """
        self.name: str = name
        self.num: int = num
