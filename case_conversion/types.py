# -*- coding: utf-8 -*-
"""Types.
"""
from enum import Enum
from enum import auto


class InvalidAcronymError(Exception):
    """Raise when acronym fails validation.
    """

    def __init__(self, acronym: str) -> None:  # noqa: D107
        """Initialization.

        Parameters
        ----------
        acronym : str
            Acronym.
        """
        msg = f"Case Conversion: acronym '{acronym}' is invalid."
        super().__init__(msg)


class Case(Enum):
    """Enum representing case types.

    Attributes
    ----------
    CAMEL : enum.auto
        First word is lower-case, the rest are title- or upper-case. String may still have separators.
    LOWER : enum.auto
        All words are lower-case.
    MIXED : enum.auto
        Any other mixing of word casing. Never occurs if there are no separators.
    PASCAL : enum.auto
        All words are title- or upper-case. String may still have separators.
    UNKNOWN : enum.auto
        String contains no words.
    UPPER : enum.auto
        All words are upper-case.
    """

    UNKNOWN = auto()
    UPPER = auto()
    LOWER = auto()
    CAMEL = auto()
    PASCAL = auto()
    MIXED = auto()
