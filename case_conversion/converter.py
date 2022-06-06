# -*- coding: utf-8 -*-
"""Converter.
"""
from typing import List
from typing import Optional

from .parser import parse_case


def camel(text: str, acronyms: Optional[List[str]] = None) -> str:
    """Return text in camelCase style.

    Parameters
    ----------
    text : str
        Input string to be converted.
    acronyms : Optional[List[str]], optional
        List of acronyms to honor.

    Returns
    -------
    str
        Case converted text.

    Examples
    --------
    >>> from python_utils.case_conversion import converter
    >>> converter.camel("hello world")
    'helloWorld'
    >>> converter.camel("HELLO_HTML_WORLD", acronyms=["HTML"])
    'helloHTMLWorld'
    """
    words, *_ = parse_case(text, acronyms=acronyms)
    if words:
        words[0] = words[0].lower()
    return "".join(words)


def pascal(text: str, acronyms: Optional[List[str]] = None) -> str:
    """Return text in PascalCase style.

    This case style is also known as: MixedCase

    Parameters
    ----------
    text : str
        Input string to be converted.
    acronyms : Optional[List[str]], optional
        List of acronyms to honor.

    Returns
    -------
    str
        Case converted text.

    Examples
    --------
    >>> converter.pascal("hello world")
    'HelloWorld'
    >>> converter.pascal("HELLO_HTML_WORLD", acronyms=["HTML"])
    'HelloHTMLWorld'
    """
    words, *_ = parse_case(text, acronyms=acronyms)
    return "".join(words)


def snake(text: str, acronyms: Optional[List[str]] = None) -> str:
    """Return text in snake_case style.

    Parameters
    ----------
    text : str
        Input string to be converted.
    acronyms : Optional[List[str]], optional
        List of acronyms to honort.

    Returns
    -------
    str
        Case converted text.

    Examples
    --------
    >>> converter.snake("hello world")
    'hello_world'
    >>> converter.snake("HelloHTMLWorld", acronyms=["HTML"])
    'hello_html_world'
    """
    words, *_ = parse_case(text, acronyms=acronyms)
    return "_".join([w.lower() for w in words])


def dash(text: str, acronyms: Optional[List[str]] = None) -> str:
    """Return text in dash-case style.

    This case style is also known as: kebab-case, spinal-case, slug-case

    Parameters
    ----------
    text : str
        Input string to be converted.
    acronyms : Optional[List[str]], optional
        List of acronyms to honor.

    Returns
    -------
    str
        Case converted text.

    Examples
    --------
    >>> converter.dash("hello world")
    'hello-world'
    >>> converter.dash("HelloHTMLWorld", acronyms=["HTML"])
    'hello-html-world'
    """
    words, *_ = parse_case(text, acronyms=acronyms)
    return "-".join([w.lower() for w in words])


def const(text: str, acronyms: Optional[List[str]] = None) -> str:
    """Return text in CONST_CASE style.

    This case style is also known as: SCREAMING_SNAKE_CASE

    Parameters
    ----------
    text : str
        Input string to be converted.
    acronyms : Optional[List[str]], optional
        List of acronyms to honor.

    Returns
    -------
    str
        Case converted text.

    Examples
    --------
    >>> converter.const("hello world")
    'HELLO_WORLD'
    >>> converter.const("helloHTMLWorld", acronyms=["HTML"])
    'HELLO_HTML_WORLD'
    """
    words, *_ = parse_case(text, acronyms=acronyms)
    return "_".join([w.upper() for w in words])


def dot(text: str, acronyms: Optional[List[str]] = None) -> str:
    """Return text in dot.case style.

    Parameters
    ----------
    text : str
        Input string to be converted.
    acronyms : Optional[List[str]], optional
        List of acronyms to honor.

    Returns
    -------
    str
        Case converted text.

    Examples
    --------
    >>> converter.dot("hello world")
    'hello.world'
    >>> converter.dot("helloHTMLWorld", acronyms=["HTML"])
    'hello.html.world'
    """
    words, *_ = parse_case(text, acronyms=acronyms)
    return ".".join([w.lower() for w in words])


def separate_words(text: str, acronyms: Optional[List[str]] = None) -> str:
    """Return text in "seperate words" style.

    Parameters
    ----------
    text : str
        Input string to be converted.
    acronyms : Optional[List[str]], optional
        List of acronyms to honor.

    Returns
    -------
    str
        Case converted text.

    Examples
    --------
    >>> converter.separate_words("HELLO_WORLD")
    'HELLO WORLD'
    >>> converter.separate_words("helloHTMLWorld", acronyms=["HTML"])
    'hello HTML World'
    """
    words, *_ = parse_case(text, acronyms=acronyms, preserve_case=True)
    return " ".join(words)


def slash(text: str, acronyms: Optional[List[str]] = None) -> str:
    """Return text in slash/case style.

    Parameters
    ----------
    text : str
        Input string to be converted.
    acronyms : Optional[List[str]], optional
        List of acronyms to honor.

    Returns
    -------
    str
        Case converted text.

    Examples
    --------
    >>> converter.slash("HELLO_WORLD")
    'HELLO/WORLD'
    >>> converter.slash("helloHTMLWorld", acronyms=["HTML"])
    'hello/HTML/World'
    """
    words, *_ = parse_case(text, acronyms=acronyms, preserve_case=True)
    return "/".join(words)


def backslash(text: str, acronyms: Optional[List[str]] = None) -> str:
    r"""Return text in backslash\case style.

    Parameters
    ----------
    text : str
        Input string to be converted.
    acronyms : Optional[List[str]], optional
        List of acronyms to honor.

    Returns
    -------
    str
        Case converted text.

    Examples
    --------
    >>> converter.backslash("HELLO_WORLD")
    'HELLO\\WORLD'
    >>> converter.backslash("helloHTMLWorld", acronyms=["HTML"])
    'hello\\HTML\\World'
    """
    words, *_ = parse_case(text, acronyms=acronyms, preserve_case=True)
    return "\\".join(words)


def ada(text: str, acronyms: Optional[List[str]] = None) -> str:
    """Return text in Ada_Case style.

    This case style is also known as: Camel_Snake.

    Parameters
    ----------
    text : str
        Input string to be converted.
    acronyms : Optional[List[str]], optional
        List of acronyms to honor.

    Returns
    -------
    str
        Case converted text.

    Examples
    --------
    >>> converter.ada("hello_world")
    'Hello_World'
    >>> converter.ada("helloHTMLWorld", acronyms=["HTML"])
    'Hello_Html_World'
    """
    words, *_ = parse_case(text, acronyms=acronyms)
    return "_".join([w.capitalize() for w in words])


def http_header(text: str, acronyms: Optional[List[str]] = None) -> str:
    """Return text in Http-Header-Case style.

    Parameters
    ----------
    text : str
        Input string to be converted.
    acronyms : Optional[List[str]], optional
        List of acronyms to honor.

    Returns
    -------
    str
        Case converted text.

    Examples
    --------
    >>> converter.http_header("hello_world")
    'Hello-World'
    >>> converter.http_header("helloHTMLWorld", acronyms=["HTML"])
    'Hello-Html-World'
    """
    words, *_ = parse_case(text, acronyms=acronyms)
    return "-".join([w.capitalize() for w in words])


def lower(text: str, *args, **kwargs) -> str:
    """Return text in lowercase style.

    This is a convenience function wrapping inbuilt lower().
    It features the same signature as other conversion functions.
    Note: Acronyms are not being honored.

    Parameters
    ----------
    text : str
        Input string to be converted.
    *args
        Placeholder to conform to common signature.
    **kwargs
        Placeholder to conform to common signature.

    Returns
    -------
    str
        Case converted text.

    Examples
    --------
    >>> converter.lower("HELLO_WORLD")
    'hello_world'
    """
    return text.lower()


def upper(text: str, *args, **kwargs) -> str:
    """Return text in UPPERCASE style.

    This is a convenience function wrapping inbuilt upper().
    It features the same signature as other conversion functions.
    Note: Acronyms are not being honored.

    Parameters
    ----------
    text : str
        Input string to be converted.
    *args
        Placeholder to conform to common signature.
    **kwargs
        Placeholder to conform to common signature.

    Returns
    -------
    str
        Case converted text.

    Examples
    --------
    >>> converter.upper("hello_world")
    'HELLO_WORLD'
    >>> converter.upper("helloHTMLWorld", acronyms=["HTML"])
    'HELLOHTMLWORLD'
    """
    return text.upper()


def title(text: str, *args, **kwargs) -> str:
    """Return text in Title_case style.

    This is a convenience function wrapping inbuilt title().
    It features the same signature as other conversion functions.
    Note: Acronyms are not being honored.

    Parameters
    ----------
    text : str
        Input string to be converted.
    *args
        Placeholder to conform to common signature.
    **kwargs
        Placeholder to conform to common signature.

    Returns
    -------
    str
        Case converted text

    Examples
    --------
    >>> converter.title("hello_world")
    'Hello_World'
    """
    return text.title()


def capital(text: str, *args, **kwargs) -> str:
    """Return text in Capital case style.

    This is a convenience function wrapping inbuilt capitalize().
    It features the same signature as other conversion functions.
    Note: Acronyms are not being honored.

    Parameters
    ----------
    text : str
        Input string to be converted.
    *args
        Placeholder to conform to common signature.
    **kwargs
        Placeholder to conform to common signature.

    Returns
    -------
    str
        Case converted text.

    Examples
    --------
    >>> converter.capital("hello_world")
    'Hello_world'
    """
    return text.capitalize()
