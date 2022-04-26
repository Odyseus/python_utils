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
    >>> camel("hello world")
    'helloWorld'
    >>> camel("HELLO_HTML_WORLD", ["HTML"])
    'helloHTMLWorld'
    """
    words, *_ = parse_case(text, acronyms)
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
    >>> pascal("hello world")
    'HelloWorld'
    >>> pascal("HELLO_HTML_WORLD", ["HTML"])
    'HelloHTMLWorld'
    """
    words, *_ = parse_case(text, acronyms)
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
    >>> snake("hello world")
    'hello_world'
    >>> snake("HelloHTMLWorld", ["HTML"])
    'hello_html_world'
    """
    words, *_ = parse_case(text, acronyms)
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
    >>> dash("hello world")
    'hello-world'
    >>> dash("HelloHTMLWorld", ["HTML"])
    'hello-html-world'
    """
    words, *_ = parse_case(text, acronyms)
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
    >>> const("hello world")
    'HELLO_WORLD'
    >>> const("helloHTMLWorld", ["HTML"])
    'HELLO_HTML_WORLD'
    """
    words, *_ = parse_case(text, acronyms)
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
    >>> dot("hello world")
    'hello.world'
    >>> dot("helloHTMLWorld", ["HTML"])
    'hello.html.world'
    """
    words, *_ = parse_case(text, acronyms)
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
    >>> separate_words("HELLO_WORLD")
    'HELLO WORLD'
    >>> separate_words("helloHTMLWorld", ["HTML"])
    'hello HTML World'
    """
    words, *_ = parse_case(text, acronyms, preserve_case=True)
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
    >>> slash("HELLO_WORLD")
    'HELLO/WORLD'
    >>> slash("helloHTMLWorld", ["HTML"])
    'hello/HTML/World'
    """
    words, *_ = parse_case(text, acronyms, preserve_case=True)
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
    >>> backslash("HELLO_WORLD")
    r'HELLO\WORLD'
    >>> backslash("helloHTMLWorld", ["HTML"])
    r'hello\HTML\World'
    """
    words, *_ = parse_case(text, acronyms, preserve_case=True)
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
    >>> ada("hello_world")
    Hello_World
    >>> ada("helloHTMLWorld", ["HTML"])
    Hello_HTML_World
    """
    words, *_ = parse_case(text, acronyms)
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
    >>> http_header("hello_world")
    Hello-World
    >>> http_header("helloHTMLWorld", ["HTML"])
    Hello-HTML-World
    """
    words, *_ = parse_case(text, acronyms)
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
    >>> lower("HELLO_WORLD")
    hello_world
    >>> lower("helloHTMLWorld", ["HTML"])
    Hello_HTML_world
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
    >>> upper("hello_world")
    HELLO_WORLD
    >>> upper("helloHTMLWorld", ["HTML"])
    Hello_HTML_world
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
    >>> title("hello_world")
    Hello_world
    >>> title("helloHTMLWorld", ["HTML"])
    Hello_HTML_world
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
    >>> capital("hello_world")
    HELLO_WORLD
    >>> capital("helloHTMLWorld", ["HTML"])
    Hello_HTML_world
    """
    return text.capitalize()
