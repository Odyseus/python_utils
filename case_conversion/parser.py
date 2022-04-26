# -*- coding: utf-8 -*-
"""Parser.
"""
from typing import List
from typing import Optional
from typing import Tuple

from .types import Case
from .utils import advanced_acronym_detection
from .utils import determine_case
from .utils import is_upper
from .utils import normalize_words
from .utils import sanitize_acronyms
from .utils import segment_string
from .utils import simple_acronym_detection


def parse_case(
    string: str, acronyms: Optional[List[str]] = None, preserve_case: bool = False,
) -> Tuple[List[str], Case, str]:
    """Split a string into words, determine its case and seperator.

    Parameters
    ----------
    string : str
        Input string to be converted
    acronyms : Optional[List[str]], optional
        List of acronyms to honor
    preserve_case : bool, optional
        Whether to preserve case of acronym

    Returns
    -------
    list of str
        Segmented input string.
    Case
        Determined case.
    str
        Determined seperator.

    Examples
    --------
    >>> parse_case("hello_world")
    ["Hello", "World"], Case.LOWER, "_"
    >>> parse_case("helloHTMLWorld", ["HTML"])
    ["Hello", "HTML", World"], Case.MIXED, None
    >>> parse_case("helloHtmlWorld", ["HTML"], True)
    ["Hello", "Html", World"], Case.CAMEL, None
    """
    words_with_sep, separator, was_upper = segment_string(string)

    if acronyms:
        # Use advanced acronym detection with list
        acronyms = sanitize_acronyms(acronyms)
        check_acronym = advanced_acronym_detection  # type: ignore
    else:
        acronyms = []
        # Fallback to simple acronym detection.
        check_acronym = simple_acronym_detection  # type: ignore

    # Letter-run detector

    # Index of current word.
    i = 0
    # Index of first letter in run.
    s = None

    # Find runs of single upper-case letters.
    while i < len(words_with_sep):
        word = words_with_sep[i]
        if word is not None and is_upper(word):
            if s is None:
                s = i
        elif s is not None:
            i = check_acronym(s, i, words_with_sep, acronyms) + 1  # type: ignore
            s = None
        i += 1

    # Separators are no longer needed, so they should be removed.
    words: List[str] = [w for w in words_with_sep if w is not None]

    # Determine case type.
    case_type = determine_case(was_upper, words, string)

    if preserve_case:
        if was_upper:
            words = [w.upper() for w in words]
    else:
        words = normalize_words(words, acronyms)

    return words, case_type, separator
