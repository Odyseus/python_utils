# -*- coding: utf-8 -*-
"""Summary
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

    from .elements import Pattern

import re

from .elements import Argument
from .elements import Command
from .elements import Either
from .elements import OneOrMore
from .elements import Option
from .elements import Optional
from .elements import OptionsShortcut
from .elements import Required
from .exceptions import DocoptExit
from .exceptions import DocoptLanguageError


class Tokens(list):
    """Summary

    Attributes
    ----------
    error : TYPE
        Description
    """

    def __init__(
        self,
        source: str | list[str],
        error: type[DocoptExit] | type[DocoptLanguageError] = DocoptExit,
    ) -> None:
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        source : str | list[str]
            Description
        error : type[DocoptExit] | type[DocoptLanguageError], optional
            Description
        """
        self += source.split() if isinstance(source, str) else source
        self.error = error

    @staticmethod
    def from_pattern(source: str) -> Tokens:
        """Summary

        Parameters
        ----------
        source : str
            Description

        Returns
        -------
        Tokens
            Description
        """
        source: str = re.sub(r"([\[\]\(\)\|]|\.\.\.)", r" \1 ", source)
        fragments: list[str] = [s for s in re.split(r"\s+|(\S*<.*?>)", source) if s]
        return Tokens(fragments, error=DocoptLanguageError)

    def move(self) -> str | None:
        """Summary

        Returns
        -------
        str | None
            Description
        """
        return self.pop(0) if len(self) else None

    def current(self) -> str | None:
        """Summary

        Returns
        -------
        str | None
            Description
        """
        return self[0] if len(self) else None


def parse_long(tokens: Tokens, options: list[Option]) -> list[Pattern]:
    """long ::= '--' chars [ ( ' ' | '=' ) chars ] ;

    Parameters
    ----------
    tokens : Tokens
        Description
    options : list[Option]
        Description

    Returns
    -------
    list[Pattern]
        Description

    Raises
    ------
    tokens.error
        Description
    """
    long, eq, value = tokens.move().partition("=")
    assert long.startswith("--")
    value: str | None = None if eq == value == "" else value
    similar: list[Option] = [o for o in options if o.long == long]
    if tokens.error is DocoptExit and similar == []:  # if no exact match
        similar = [o for o in options if o.long and o.long.startswith(long)]

    o: Option | None = None

    if len(similar) > 1:  # might be simply specified ambiguously 2+ times?
        raise tokens.error(
            "%s is not a unique prefix: %s?" % (long, ", ".join(o.long for o in similar))
        )
    elif len(similar) < 1:
        argcount: int = 1 if eq == "=" else 0
        o = Option(None, long, argcount)
        options.append(o)
        if tokens.error is DocoptExit:
            o = Option(None, long, argcount, value if argcount else True)
    else:
        o = Option(similar[0].short, similar[0].long, similar[0].argcount, similar[0].value)
        if o.argcount == 0:
            if value is not None:
                raise tokens.error("%s must not have an argument" % o.long)
        else:
            if value is None:
                if tokens.current() in [None, "--"]:
                    raise tokens.error("%s requires argument" % o.long)
                value = tokens.move()
        if tokens.error is DocoptExit:
            o.value = value if value is not None else True
    return [o]


def parse_shorts(tokens: Tokens, options: list[Option]) -> list[Pattern]:
    """shorts ::= '-' ( chars )* [ [ ' ' ] chars ] ;

    Parameters
    ----------
    tokens : Tokens
        Description
    options : list[Option]
        Description

    Returns
    -------
    list[Pattern]
        Description

    Raises
    ------
    tokens.error
        Description
    """
    token: str = tokens.move()
    assert token.startswith("-") and not token.startswith("--")
    left: str = token.lstrip("-")
    parsed: list[Pattern] = []
    while left != "":
        short, left = "-" + left[0], left[1:]
        similar: list[Option] = [o for o in options if o.short == short]
        o: Option | None = None

        if len(similar) > 1:
            raise tokens.error("%s is specified ambiguously %d times" % (short, len(similar)))
        elif len(similar) < 1:
            o = Option(short, None, 0)
            options.append(o)
            if tokens.error is DocoptExit:
                o = Option(short, None, 0, True)
        else:  # why copying is necessary here?
            o = Option(short, similar[0].long, similar[0].argcount, similar[0].value)
            value: str | None = None
            if o.argcount != 0:
                if left == "":
                    if tokens.current() in [None, "--"]:
                        raise tokens.error("%s requires argument" % short)
                    value = tokens.move()
                else:
                    value = left
                    left = ""
            if tokens.error is DocoptExit:
                o.value = value if value is not None else True
        parsed.append(o)
    return parsed


def parse_pattern(source: str, options: list[Option]) -> Required:
    """Summary

    Parameters
    ----------
    source : str
        Description
    options : list[Option]
        Description

    Returns
    -------
    Required
        Description

    Raises
    ------
    tokens.error
        Description
    """
    tokens: Tokens = Tokens.from_pattern(source)
    result: list[Pattern] = parse_expr(tokens, options)
    if tokens.current() is not None:
        raise tokens.error("unexpected ending: %r" % " ".join(tokens))
    return Required(*result)


def parse_expr(tokens: Tokens, options: list[Option]) -> list[Pattern]:
    """expr ::= seq ( '|' seq )* ;

    Parameters
    ----------
    tokens : Tokens
        Description
    options : list[Option]
        Description

    Returns
    -------
    list[Pattern]
        Description
    """
    seq: list[Pattern] = parse_seq(tokens, options)
    if tokens.current() != "|":
        return seq
    result: list[Pattern] = [Required(*seq)] if len(seq) > 1 else seq
    while tokens.current() == "|":
        tokens.move()
        seq = parse_seq(tokens, options)
        result += [Required(*seq)] if len(seq) > 1 else seq
    return [Either(*result)] if len(result) > 1 else result


def parse_seq(tokens: Tokens, options: list[Option]) -> list[Pattern]:
    """seq ::= ( atom [ '...' ] )* ;

    Parameters
    ----------
    tokens : Tokens
        Description
    options : list[Option]
        Description

    Returns
    -------
    list[Pattern]
        Description
    """
    result: list[Pattern] = []
    while tokens.current() not in [None, "]", ")", "|"]:
        atom: list = parse_atom(tokens, options)
        if tokens.current() == "...":
            atom = [OneOrMore(*atom)]
            tokens.move()
        result += atom
    return result


def parse_atom(tokens: Tokens, options: list[Option]) -> list[Pattern]:
    """atom ::= '(' expr ')' | '[' expr ']' | 'options'
    | long | shorts | argument | command ;

    Parameters
    ----------
    tokens : Tokens
        Description
    options : list[Option]
        Description

    Returns
    -------
    list[Pattern]
        Description

    Raises
    ------
    tokens.error
        Description
    """
    token: str = tokens.current()
    result: Pattern = []  # type: ignore[assignment]
    if token in "([":
        tokens.move()
        matching, pattern = {"(": [")", Required], "[": ["]", Optional]}[token]
        result = pattern(*parse_expr(tokens, options))  # type: ignore[operator]
        if tokens.move() != matching:
            raise tokens.error("unmatched '%s'" % token)
        return [result]
    elif token == "options":
        tokens.move()
        return [OptionsShortcut()]
    elif token.startswith("--") and token != "--":
        return parse_long(tokens, options)
    elif token.startswith("-") and token not in ("-", "--"):
        return parse_shorts(tokens, options)
    elif token.startswith("<") and token.endswith(">") or token.isupper():
        return [Argument(tokens.move())]
    else:
        return [Command(tokens.move())]


def parse_argv(tokens: Tokens, options: list[Option], options_first: bool = False) -> list[Any]:
    """Parse command-line argument vector.

    If options_first:
        argv ::= [ long | shorts ]* [ argument ]* [ '--' [ argument ]* ] ;

    Parameters
    ----------
    tokens : Tokens
        Description
    options : list[Option]
        Description
    options_first : bool, optional
        Description

    Returns
    -------
    list[Any]
        Description

    else
    ----
    argv ::= [ long | shorts | argument ]* [ '--' [ argument ]* ] ;

    """
    parsed: list[Any] = []
    while tokens.current() is not None:
        if tokens.current() == "--":
            return parsed + [Argument(None, v) for v in tokens]
        elif tokens.current().startswith("--"):
            parsed += parse_long(tokens, options)
        elif tokens.current().startswith("-") and tokens.current() != "-":
            parsed += parse_shorts(tokens, options)
        elif options_first:
            return parsed + [Argument(None, v) for v in tokens]
        else:
            parsed.append(Argument(None, tokens.move()))
    return parsed


def parse_defaults(doc: str) -> list[Option]:
    """Summary

    Parameters
    ----------
    doc : str
        Description

    Returns
    -------
    list[Option]
        Description
    """
    defaults: list[Option] = []

    for s in parse_section("options", doc):
        # split: list[str] = re.split(r"\n *(<\S+?>|-\S+?)", "\n" + s)[1:]
        split: list[str] = re.split(r"\n[ \t]*(-\S+?)", "\n" + s)[1:]
        split = [s1 + s2 for s1, s2 in zip(split[::2], split[1::2])]
        options: list[Option] = [Option.parse(s) for s in split if s.startswith("-")]
        defaults += options
    return defaults


def parse_section(name: str, source: str) -> list[str]:
    """Summary

    Parameters
    ----------
    name : str
        Description
    source : str
        Description

    Returns
    -------
    list[str]
        Description
    """
    print
    pattern = re.compile(
        r"(?<=(^\<{0}\>$))([\s\S]*?)(?=(^\<\/{0}\>$))".format(name), flags=re.MULTILINE
    )

    return [s[1] for s in pattern.findall(source)]
