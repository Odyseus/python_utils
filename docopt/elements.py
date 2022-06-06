# -*- coding: utf-8 -*-
"""Elements.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

import re


class Pattern(object):
    """Summary

    Attributes
    ----------
    value : TYPE
        Description
    """

    def __init__(self, name: str | None, value: list[str] | str | int | None = None) -> None:
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        name : str | None
            Description
        value : list[str] | str | int | None, optional
            Description
        """
        self._name = name
        self.value = value

    @property
    def name(self) -> str | None:
        """Summary

        Returns
        -------
        str | None
            Description
        """
        return self._name

    def __eq__(self, other: Any) -> bool:
        """See :py:meth:`object.__eq__`.

        Parameters
        ----------
        other : Any
            Description

        Returns
        -------
        bool
            Description
        """
        return repr(self) == repr(other)

    def __hash__(self) -> int:
        """See :py:meth:`object.__hash__`.

        Returns
        -------
        int
            Description
        """
        return hash(repr(self))


def transform(pattern: BranchPattern) -> Either:
    """Expand pattern into an (almost) equivalent one, but with single Either.

    Example: ((-a | -b) (-c | -d)) => (-a -c | -a -d | -b -c | -b -d)
    Quirks: [-a] => (-a), (-a...) => (-a -a)

    Parameters
    ----------
    pattern : BranchPattern
        Description

    Returns
    -------
    Either
        Description

    """
    result: list[list[BranchPattern]] = []
    groups: list[list[BranchPattern]] = [[pattern]]
    while groups:
        children: list[BranchPattern] = groups.pop(0)
        parents: list[type[BranchPattern]] = [
            Required,
            Optional,
            OptionsShortcut,
            Either,
            OneOrMore,
        ]
        if any(t in map(type, children) for t in parents):
            child: BranchPattern = [c for c in children if type(c) in parents][0]
            children.remove(child)
            if type(child) is Either:
                for c in child.children:
                    groups.append([c] + children)
            elif type(child) is OneOrMore:
                groups.append(child.children * 2 + children)
            else:
                groups.append(child.children + children)
        else:
            result.append(children)
    return Either(*[Required(*e) for e in result])


class LeafPattern(Pattern):

    """Leaf/terminal node of a pattern tree.

    Deleted Attributes
    ------------------
    name : TYPE
        Description
    value : TYPE
        Description
    """

    def __repr__(self) -> str:
        """See :py:meth:`object.__repr__`.

        Returns
        -------
        str
            Description
        """
        return "%s(%r, %r)" % (self.__class__.__name__, self.name, self.value)

    def single_match(self, left: list[LeafPattern]) -> tuple[int | None, LeafPattern | None]:
        """Summary

        Parameters
        ----------
        left : list[LeafPattern]
            Description

        Raises
        ------
        NotImplementedError
            Description
        """
        raise NotImplementedError

    def flat(self, *types) -> list[LeafPattern]:
        """Summary

        Parameters
        ----------
        *types
            Description

        Returns
        -------
        list[LeafPattern]
            Description
        """
        return [self] if not types or type(self) in types else []

    def match(
        self, left: list[LeafPattern], collected: list[Pattern] = None
    ) -> tuple[bool, list[LeafPattern], list[Pattern]]:
        """Summary

        Parameters
        ----------
        left : list[LeafPattern]
            Description
        collected : list[Pattern], optional
            Description

        Returns
        -------
        tuple[bool, list[LeafPattern], list[Pattern]]
            Description
        """
        collected = [] if collected is None else collected
        increment: Any | None = None
        pos, match = self.single_match(left)
        if match is None or pos is None:
            return False, left, collected
        left_ = left[:pos] + left[(pos + 1):]
        same_name = [a for a in collected if a.name == self.name]
        if type(self.value) == int and len(same_name) > 0:
            if isinstance(same_name[0].value, int):
                same_name[0].value += 1
            return True, left_, collected
        if type(self.value) == int and not same_name:
            match.value = 1
            return True, left_, collected + [match]
        if same_name and type(self.value) == list:
            if type(match.value) == str:
                increment = [match.value]
            if same_name[0].value is not None and increment is not None:
                if isinstance(same_name[0].value, type(increment)):
                    same_name[0].value += increment
            return True, left_, collected
        elif not same_name and type(self.value) == list:
            if isinstance(match.value, str):
                match.value = [match.value]
            return True, left_, collected + [match]
        return True, left_, collected + [match]


class BranchPattern(Pattern):

    """Branch/inner node of a pattern tree.

    Attributes
    ----------
    children : list
        Description
    """

    def __init__(self, *children) -> None:
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        *children
            Description
        """
        self.children: list = list(children)

    def match(self, left: list[Pattern], collected: list[Pattern] = None) -> Any:
        """Summary

        Parameters
        ----------
        left : list[Pattern]
            Description
        collected : list[Pattern], optional
            Description

        Raises
        ------
        NotImplementedError
            Description
        """
        raise NotImplementedError

    def fix(self) -> BranchPattern:
        """Summary

        Returns
        -------
        BranchPattern
            Description
        """
        self.fix_identities()
        self.fix_repeating_arguments()
        return self

    def fix_identities(self, uniq: Any | None = None) -> BranchPattern | None:
        """Make pattern-tree tips point to same object if they are equal.

        Parameters
        ----------
        uniq : Any | None, optional
            Description

        Returns
        -------
        BranchPattern | None
            Description
        """
        if not hasattr(self, "children"):
            return self
        uniq = list(set(self.flat())) if uniq is None else uniq
        for i, child in enumerate(self.children):
            if not hasattr(child, "children"):
                assert child in uniq
                self.children[i] = uniq[uniq.index(child)]
            else:
                child.fix_identities(uniq)

        return None

    def fix_repeating_arguments(self) -> BranchPattern:
        """Fix elements that should accumulate/increment values.

        Returns
        -------
        BranchPattern
            Description
        """
        either: list = [list(child.children) for child in transform(self).children]
        for case in either:
            for e in [child for child in case if case.count(child) > 1]:
                if type(e) is Argument or type(e) is Option and e.argcount:
                    if e.value is None:
                        e.value = []
                    elif type(e.value) is not list:
                        e.value = e.value.split()  # type: ignore[union-attr]
                if type(e) is Command or type(e) is Option and e.argcount == 0:
                    e.value = 0

        return self

    def __repr__(self) -> str:
        """See :py:meth:`object.__repr__`.

        Returns
        -------
        str
            Description
        """
        return "%s(%s)" % (self.__class__.__name__, ", ".join(repr(a) for a in self.children))

    def flat(self, *types) -> Any:
        """Summary

        Parameters
        ----------
        *types
            Description

        Returns
        -------
        Any
            Description
        """
        if type(self) in types:
            return [self]
        return sum([child.flat(*types) for child in self.children], [])


class Argument(LeafPattern):
    """Summary"""

    def single_match(self, left: list[LeafPattern]) -> tuple[int | None, LeafPattern | None]:
        """Summary

        Parameters
        ----------
        left : list[LeafPattern]
            Description

        Returns
        -------
        tuple[int | None, LeafPattern | None]
            Description
        """
        for n, pattern in enumerate(left):
            if type(pattern) is Argument:
                return n, Argument(self.name, pattern.value)
        return None, None

    @classmethod
    def parse(cls, source: str) -> Argument:
        """Summary

        Parameters
        ----------
        source : str
            Description

        Returns
        -------
        Argument
            Description

        Deleted Parameters
        ------------------
        cls : TYPE
            Description
        """
        name: str = re.findall(r"(<\S*?>)", source)[0]
        value: list[str] = re.findall(r"\[default: (.*)\]", source, flags=re.I)
        return cls(name, value[0] if value else None)


class Command(Argument):
    """Summary

    Attributes
    ----------
    value : bool
        Description

    Deleted Attributes
    ------------------
    name : str
        Description
    """

    def __init__(self, name: str | None, value: bool = False) -> None:
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        name : str | None
            Description
        value : bool, optional
            Description
        """
        self._name: str = name
        self.value: bool = value

    def single_match(self, left: list[LeafPattern]) -> tuple[int | None, LeafPattern | None]:
        """Summary

        Parameters
        ----------
        left : list[LeafPattern]
            Description

        Returns
        -------
        tuple[int | None, LeafPattern | None]
            Description
        """
        for n, pattern in enumerate(left):
            if type(pattern) is Argument:
                if pattern.value == self.name:
                    return n, Command(self.name, True)
                else:
                    break
        return None, None


class Option(LeafPattern):
    """Summary

    Attributes
    ----------
    argcount : int
        Description
    long : str | None
        Description
    short : str | None
        Description
    value : list[str] | str | int | None
        Description
    """

    def __init__(
        self,
        short: str | None = None,
        long: str | None = None,
        argcount: int = 0,
        value: list[str] | str | int | None = False,
    ) -> None:
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        short : str | None, optional
            Description
        long : str | None, optional
            Description
        argcount : int, optional
            Description
        value : list[str] | str | int | None, optional
            Description
        """
        assert argcount in (0, 1)
        self.short: str | None = short
        self.long: str | None = long
        self.argcount: int = argcount
        self.value: list[str] | str | int | None = None if value is False and argcount else value

    @classmethod
    def parse(cls, option_description: str) -> Option:
        """Summary

        Parameters
        ----------
        option_description : str
            Description

        Returns
        -------
        Option
            Description

        Deleted Parameters
        ------------------
        cls : TYPE
            Description
        """
        short: str | None = None
        long: str | None = None
        argcount: int = 0
        value: list[str] | str | int | None = False
        options, _, description = option_description.strip().partition("  ")
        options: str = options.replace(",", " ").replace("=", " ")
        for s in options.split():
            if s.startswith("--"):
                long = s
            elif s.startswith("-"):
                short = s
            else:
                argcount = 1
        if argcount:
            matched: list[str] = re.findall(r"\[default: (.*)\]", description, flags=re.I)
            value: str | None = matched[0] if matched else None
        return cls(short, long, argcount, value)

    def single_match(self, left: list[LeafPattern]) -> tuple[int | None, LeafPattern | None]:
        """Summary

        Parameters
        ----------
        left : list[LeafPattern]
            Description

        Returns
        -------
        tuple[int | None, LeafPattern | None]
            Description
        """
        for n, pattern in enumerate(left):
            if self.name == pattern.name:
                return n, pattern
        return None, None

    @property
    def name(self) -> str | None:
        """Summary

        Returns
        -------
        str | None
            Description
        """
        return self.long or self.short

    def __repr__(self) -> str:
        """See :py:meth:`object.__repr__`.

        Returns
        -------
        str
            Description
        """
        return "Option(%r, %r, %r, %r)" % (self.short, self.long, self.argcount, self.value)


class Required(BranchPattern):
    """Summary"""

    def match(self, left: list[Pattern], collected: list[Pattern] = None) -> Any:
        """Summary

        Parameters
        ----------
        left : list[Pattern]
            Description
        collected : list[Pattern], optional
            Description

        Returns
        -------
        Any
            Description
        """
        collected = [] if collected is None else collected
        l: list[Pattern] = left  # noqa: E741
        c: list[Pattern] = collected
        for pattern in self.children:
            matched, l, c = pattern.match(l, c)
            if not matched:
                return False, left, collected
        return True, l, c


class Optional(BranchPattern):
    """Summary"""

    def match(self, left: list[Pattern], collected: list[Pattern] | None = None) -> Any:
        """Summary

        Parameters
        ----------
        left : list[Pattern]
            Description
        collected : list[Pattern] | None, optional
            Description

        Returns
        -------
        Any
            Description
        """
        collected = [] if collected is None else collected
        for pattern in self.children:
            m, left, collected = pattern.match(left, collected)
        return True, left, collected


class OptionsShortcut(Optional):

    """Marker/placeholder for [options] shortcut."""


class OneOrMore(BranchPattern):
    """Summary"""

    def match(
        self, left: list[Pattern], collected: list[Pattern] | None = None
    ) -> tuple[bool, list[Pattern], list[Pattern]]:
        """Summary

        Parameters
        ----------
        left : list[Pattern]
            Description
        collected : list[Pattern] | None, optional
            Description

        Returns
        -------
        tuple[bool, list[Pattern], list[Pattern]]
            Description
        """
        assert len(self.children) == 1
        collected = [] if collected is None else collected
        l: list[Pattern] = left  # noqa: E741
        c: list[Pattern] | None = collected
        l_: list[Pattern] | None = None
        matched: bool = True
        times: int = 0
        while matched:
            # could it be that something didn't match but changed l or c?
            matched, l, c = self.children[0].match(l, c)
            times += 1 if matched else 0
            if l_ == l:
                break
            l_ = l
        if times >= 1:
            return True, l, c
        return False, left, collected


class Either(BranchPattern):
    """Summary"""

    def match(
        self, left: list[Pattern], collected: list[Pattern] = None
    ) -> tuple[bool, list[Pattern], list[Pattern]]:
        """Summary

        Parameters
        ----------
        left : list[Pattern]
            Description
        collected : list[Pattern], optional
            Description

        Returns
        -------
        tuple[bool, list[Pattern], list[Pattern]]
            Description
        """
        collected = [] if collected is None else collected
        outcomes: list[tuple[bool, list[Pattern], list[Pattern]]] = []
        for pattern in self.children:
            matched, _, _ = outcome = pattern.match(left, collected)
            if matched:
                outcomes.append(outcome)
        if outcomes:
            return min(outcomes, key=lambda outcome: len(outcome[1]))
        return False, left, collected


class ParsedOptionsAttrs:
    """Summary"""

    def __init__(self, args_dict: ParsedOptionsDict) -> None:
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        args_dict : ParsedOptionsDict
            Description

        Raises
        ------
        AttributeError
            Description
        """
        for k, v in args_dict.items():
            attr: str = self._arg_to_attr(k)

            if hasattr(self, attr):
                raise AttributeError(
                    f"The '{k}' key produced the '{attr}' attribute which already exists."
                )

            setattr(self, attr, v)

    def _arg_to_attr(self, arg: str) -> str:
        """Summary

        Parameters
        ----------
        arg : str
            Description

        Returns
        -------
        str
            Description
        """
        return arg.strip("-<>").replace("-", "_")


class ParsedOptionsDict(dict):
    """Summary

    .. code-block::

        Usage:
            my_program (get | clear) [--update]

    """

    def get_attributes(self) -> ParsedOptionsAttrs:
        """Summary

        Returns
        -------
        ParsedOptionsAttrs
            Description
        """
        return ParsedOptionsAttrs(self)

    def __repr__(self) -> str:
        """See :py:meth:`object.__repr__`.

        Returns
        -------
        str
            Description
        """
        return "{%s}" % ",\n ".join("%r: %r" % i for i in sorted(self.items()))
