# -*- coding: utf-8 -*-
"""Titlecase.

- Original Perl version by: John Gruber http://daringfireball.net/ 10 May 2008
- Python version by Stuart Colville http://muffinresearch.co.uk
- License: http://www.opensource.org/licenses/mit-license.php

.. note::
    This is a slightly modified version of the
    `titlecase module <https://github.com/ppannuto/python-titlecase>`__.

    **Modifications**:

    - Removed command line parser and associated functions.
    - Moved tests to docstrings to be able to run them with ``doctest``.

Attributes
----------
APOS_SECOND : re.Pattern
    Compiled regular expression to match apostrophe.
CAPFIRST : re.Pattern
    Compiled regular expression to match capital first (?).
CONSONANTS : re.Pattern
    Compiled regular expression to match consonants.
INLINE_PERIOD : re.Pattern
    Compiled regular expression to match in-line period.
MAC_MC : re.Pattern
    Compiled regular expression to match Mac/Mc.
MR_MRS_MS_DR : re.Pattern
    Compiled regular expression to match Mr/Mrs/Ms/Dr.
PUNCT : str
    String to match punctuation characters.
SMALL : str
    Default *small* words.
SMALL_FIRST : re.Pattern
    Compiled regular expression to match small words **before** punctuation characters.
SMALL_LAST : re.Pattern
    Compiled regular expression to match small words **after** punctuation characters.
SMALL_WORDS : re.Pattern
    Compiled regular expression to match small words.
SUBPHRASE : re.Pattern
    Compiled regular expression to match sub-phases starting with a small word.
UC_ELSEWHERE : re.Pattern
    Compiled regular expression to match something (?).
UC_INITIALS : re.Pattern
    Compiled regular expression to match what could be interpreted as initials.

Examples
--------

>>> from python_utils.titlecase import titlecase, set_small_word_list, UC_INITIALS

>>> titlecase("")
''

>>> titlecase("word/word")
'Word/Word'

>>> titlecase("a title and/or string")
'A Title and/or String'

>>> titlecase("dance with me/let’s face the music and dance")
'Dance With Me/Let’s Face the Music and Dance'

>>> titlecase("a-b end-to-end two-not-three/three-by-four/five-and")
'A-B End-to-End Two-Not-Three/Three-by-Four/Five-And'

>>> titlecase("34th 3rd 2nd")
'34th 3rd 2nd'

>>> titlecase("Q&A with steve jobs: 'that's what happens in technology'")
"Q&A With Steve Jobs: 'That's What Happens in Technology'"

>>> titlecase("What is AT&T's problem?")
"What Is AT&T's Problem?"

>>> titlecase("Apple deal with AT&T falls through")
'Apple Deal With AT&T Falls Through'

>>> titlecase("Words with all consonants like cnn are acronyms")
'Words With All Consonants Like CNN Are Acronyms'

>>> titlecase("this v that")
'This v That'

>>> titlecase("this v. that")
'This v. That'

>>> titlecase("this vs that")
'This vs That'

>>> titlecase("this vs. that")
'This vs. That'

>>> titlecase("The SEC's Apple probe: what you need to know")
"The SEC's Apple Probe: What You Need to Know"

>>> titlecase("'by the Way, small word at the start but within quotes.'")
"'By the Way, Small Word at the Start but Within Quotes.'"

>>> titlecase("Small word at end is nothing to be afraid of")
'Small Word at End Is Nothing to Be Afraid Of'

>>> titlecase("Starting Sub-Phrase With a Small Word: a Trick, Perhaps?")
'Starting Sub-Phrase With a Small Word: A Trick, Perhaps?'

>>> titlecase("Sub-Phrase With a Small Word in Quotes: 'a Trick, Perhaps?'")
"Sub-Phrase With a Small Word in Quotes: 'A Trick, Perhaps?'"

>>> titlecase('sub-phrase with a small word in quotes: "a trick, perhaps?"')
'Sub-Phrase With a Small Word in Quotes: "A Trick, Perhaps?"'

>>> titlecase("Starting a Hyphen Delimited Sub-Phrase With a Small Word - a Trick, Perhaps?")
'Starting a Hyphen Delimited Sub-Phrase With a Small Word - A Trick, Perhaps?'

>>> titlecase("Hyphen Delimited Sub-Phrase With a Small Word in Quotes - 'a Trick, Perhaps?'")
"Hyphen Delimited Sub-Phrase With a Small Word in Quotes - 'A Trick, Perhaps?'"

>>> titlecase('Hyphen Delimited sub-phrase with a small word in quotes - "a trick, perhaps?"')
'Hyphen Delimited Sub-Phrase With a Small Word in Quotes - "A Trick, Perhaps?"'

>>> titlecase("Snakes on a Plane - The TV Edit - The Famous Line")
'Snakes on a Plane - The TV Edit - The Famous Line'

>>> titlecase("Starting an Em Dash Delimited Sub-Phrase With a Small Word — a Trick, Perhaps?")
'Starting an Em Dash Delimited Sub-Phrase With a Small Word — A Trick, Perhaps?'

>>> titlecase("Em Dash Delimited Sub-Phrase With a Small Word in Quotes — 'a Trick, Perhaps?'")
"Em Dash Delimited Sub-Phrase With a Small Word in Quotes — 'A Trick, Perhaps?'"

>>> titlecase('Em Dash Delimited sub-phrase with a small word in quotes — "a trick, perhaps?"')
'Em Dash Delimited Sub-Phrase With a Small Word in Quotes — "A Trick, Perhaps?"'

>>> titlecase("Snakes on a Plane — The TV Edit — The Famous Line")
'Snakes on a Plane — The TV Edit — The Famous Line'

>>> titlecase("EPISODE 7 — THE FORCE AWAKENS")
'Episode 7 — The Force Awakens'

>>> titlecase("episode 7 – The force awakens")
'Episode 7 – The Force Awakens'

>>> titlecase("THE CASE OF X ≤ 7")
'The Case of X ≤ 7'

>>> titlecase("the case of X ≤ 7")
'The Case of X ≤ 7'

>>> titlecase('"Nothing to Be Afraid of?"')
'"Nothing to Be Afraid Of?"'

>>> titlecase('"Nothing to be Afraid Of?"')
'"Nothing to Be Afraid Of?"'

>>> titlecase("a thing")
'A Thing'

>>> titlecase("2lmc Spool: 'gruber on OmniFocus and vapo(u)rware'")
"2lmc Spool: 'Gruber on OmniFocus and Vapo(u)rware'"

>>> titlecase("this is just an example.com")
'This Is Just an example.com'

>>> titlecase("this is something listed on del.icio.us")
'This Is Something Listed on del.icio.us'

>>> titlecase("iTunes should be unmolested")
'iTunes Should Be Unmolested'

>>> titlecase("reading between the lines of steve jobs’s ‘thoughts on music’")
'Reading Between the Lines of Steve Jobs’s ‘Thoughts on Music’'

>>> titlecase("seriously, ‘repair permissions’ is voodoo")
'Seriously, ‘Repair Permissions’ Is Voodoo'

>>> titlecase("generalissimo francisco franco: still dead; kieren McCarthy: still a jackass")
'Generalissimo Francisco Franco: Still Dead; Kieren McCarthy: Still a Jackass'

>>> titlecase("O'Reilly should be untouched")
"O'Reilly Should Be Untouched"

>>> titlecase("my name is o'reilly")
"My Name Is O'Reilly"

>>> titlecase("WASHINGTON, D.C. SHOULD BE FIXED BUT MIGHT BE A PROBLEM")
'Washington, D.C. Should Be Fixed but Might Be a Problem'

>>> titlecase("THIS IS ALL CAPS AND SHOULD BE ADDRESSED")
'This Is All Caps and Should Be Addressed'

>>> titlecase("Mr McTavish went to MacDonalds")
'Mr McTavish Went to MacDonalds'

>>> titlecase("this shouldn't\\nget mangled")
"This Shouldn't\\nGet Mangled"

>>> titlecase("this is http://foo.com")
'This Is http://foo.com'

>>> titlecase("mac mc MAC MC machine")
'Mac Mc MAC MC Machine'

>>> titlecase("FOO BAR 5TH ST")
'Foo Bar 5th St'

>>> titlecase("foo bar 5th st")
'Foo Bar 5th St'

>>> titlecase("l'grange l'grange l'Grange l'Grange")
"l'Grange l'Grange l'Grange l'Grange"

>>> titlecase("L'grange L'grange L'Grange L'Grange")
"l'Grange l'Grange l'Grange l'Grange"

>>> titlecase("l'GranGe")
"l'GranGe"

>>> titlecase("o'grange O'grange o'Grange O'Grange")
"O'Grange O'Grange O'Grange O'Grange"

>>> titlecase("o'grange's O'grange's o'Grange's O'Grange's")
"O'Grange's O'Grange's O'Grange's O'Grange's"

>>> titlecase("O'GranGe")
"O'GranGe"

>>> titlecase("o'melveny/o'doyle o'Melveny/o'doyle O'melveny/o'doyle o'melveny/o'Doyle o'melveny/O'doyle")
"O'Melveny/O'Doyle O'Melveny/O'Doyle O'Melveny/O'Doyle O'Melveny/O'Doyle O'Melveny/O'Doyle"

>>> titlecase("mccay-mcbut-mcdo mcdonalds/mcby")
'McCay-McBut-McDo McDonalds/McBy'

>>> titlecase("oblon, spivak, mcclelland, maier & neustadt")
'Oblon, Spivak, McClelland, Maier & Neustadt'

>>> titlecase("Mcoblon, spivak, mcclelland, mcmaier, & mcneustadt")
'McOblon, Spivak, McClelland, McMaier, & McNeustadt'

>>> titlecase("mcfoo-bar, MCFOO-BAR, McFoo-bar, McFoo-Bar, mcfoo-mcbar, foo-mcbar")
'McFoo-Bar, McFoo-Bar, McFoo-Bar, McFoo-Bar, McFoo-McBar, Foo-McBar'

>>> titlecase("'QUOTE' A GREAT")
"'Quote' a Great"

>>> titlecase("‘QUOTE’ A GREAT")
'‘Quote’ a Great'

>>> titlecase("“YOUNG AND RESTLESS”")
'“Young and Restless”'

>>> titlecase("EL NIÑO A ARRIVÉ HIER")
'El Niño a Arrivé Hier'

>>> titlecase("YEA NO")
'Yea No'

>>> titlecase("ÝÆ ÑØ")
'Ýæ Ñø'

>>> titlecase("yea no")
'Yea No'

>>> titlecase("ýæ ñø")
'Ýæ Ñø'

>>> titlecase("Mr mr Mrs Ms Mss Dr dr , Mr. and Mrs. Person")
'Mr Mr Mrs Ms MSS Dr Dr , Mr. And Mrs. Person'

Test callback.

>>> def abbreviation(word, **kwargs):
...     if word.upper() in ("TCP", "UDP"):
...         return word.upper()
>>> s = "a simple tcp and udp wrapper"
>>> titlecase(s)
'A Simple TCP and Udp Wrapper'
>>> titlecase(s, callback=abbreviation)
'A Simple TCP and UDP Wrapper'
>>> titlecase(s.upper(), callback=abbreviation)
'A Simple TCP and UDP Wrapper'
>>> titlecase("crème brûlée", callback=lambda x, **kw: x.upper())
'CRÈME BRÛLÉE'

Test initials.

>>> bool(UC_INITIALS.match("A.B"))
True
>>> bool(UC_INITIALS.match("A.B."))
True
>>> bool(UC_INITIALS.match("ABCD"))
False

Test ``set_small_word_list``.

>>> titlecase('playing the game "words with friends"')
'Playing the Game "Words With Friends"'
>>> set_small_word_list("a|an|the|with")
>>> titlecase('playing the game "words with friends"')
'Playing the Game "Words with Friends"'

"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

import re


__all__ = ["titlecase"]
__version__ = "2.3.0"

SMALL: str = r"a|an|and|as|at|but|by|en|for|if|in|of|on|or|the|to|v\.?|via|vs\.?"
PUNCT: str = r"""!"“#$%&'‘()*+,\-–‒—―./:;?@[\\\]_`{|}~"""

CONSONANTS: re.Pattern = re.compile(r"\A[cnpshgdkljrwqvxtfbmz]+\Z", flags=re.IGNORECASE)
SMALL_WORDS: re.Pattern = re.compile(r"^(%s)$" % SMALL, flags=re.IGNORECASE)
SMALL_FIRST: re.Pattern = re.compile(r"^([%s]*)(%s)\b" % (PUNCT, SMALL), flags=re.IGNORECASE)
SMALL_LAST: re.Pattern = re.compile(r"\b(%s)[%s]?$" % (SMALL, PUNCT), flags=re.IGNORECASE)
SUBPHRASE: re.Pattern = re.compile(r"([:.;?!\-–‒—―][ ])(%s)" % SMALL)
MAC_MC: re.Pattern = re.compile(r"^([Mm]c|MC)(\w.+)")
MR_MRS_MS_DR: re.Pattern = re.compile(r"^((m((rs?)|s))|Dr)$", flags=re.IGNORECASE)
INLINE_PERIOD: re.Pattern = re.compile(r"[\w][.][\w]", flags=re.IGNORECASE)
UC_ELSEWHERE: re.Pattern = re.compile(r"[%s]*?[a-zA-Z]+[A-Z]+?" % PUNCT)
CAPFIRST: re.Pattern = re.compile(r"^[%s]*?([\w])" % PUNCT)
APOS_SECOND: re.Pattern = re.compile(r"^[dol]['‘][\w]+(?:['s]{2})?$", flags=re.IGNORECASE)
UC_INITIALS: re.Pattern = re.compile(r"^(?:[A-Z]\.|[A-Z]\.[A-Z])+$")


class Immutable(object):
    """Immutable object."""

    pass


class ImmutableString(str, Immutable):
    """Immutable string."""

    pass


class ImmutableBytes(bytes, Immutable):
    """Immutable bytes."""

    pass


def _mark_immutable(text: str | bytes) -> ImmutableBytes | ImmutableString:
    """If a callback has done something specific, leave this string alone from now on.

    Parameters
    ----------
    text : str | bytes
        Text to mark as immutable.

    Returns
    -------
    ImmutableBytes | ImmutableString
        Immutable text.
    """
    if isinstance(text, bytes):
        return ImmutableBytes(text)
    return ImmutableString(text)


def set_small_word_list(small: str = SMALL) -> None:
    """Set a new list of small words to override the ones defined in :py:attr:`titlecase.SMALL`.

    Parameters
    ----------
    small : str, optional
        New list of small words. See :py:attr:`titlecase.SMALL`.
    """
    global SMALL_WORDS
    global SMALL_FIRST
    global SMALL_LAST
    global SUBPHRASE
    SMALL_WORDS = re.compile(r"^(%s)$" % small, re.I)
    SMALL_FIRST = re.compile(r"^([%s]*)(%s)\b" % (PUNCT, small), re.I)
    SMALL_LAST = re.compile(r"\b(%s)[%s]?$" % (small, PUNCT), re.I)
    SUBPHRASE = re.compile(r"([:.;?!][ ])(%s)" % small)


def titlecase(text: str, callback: Callable[..., str] = None, small_first_last: bool = True) -> str:
    """This filter changes all words to Title Caps, and attempts to be clever
    about un-capitalizing SMALL words like a/an/the in the input.

    The list of "SMALL words" which are not capped comes from
    the New York Times Manual of Style, plus 'vs' and 'v'.

    Parameters
    ----------
    text : str
        Titlecases input text.
    callback : Callable[..., str], optional
        Callback function that returns the titlecase version of a specific word.
    small_first_last : bool, optional
        Capitalize small words (e.g. 'A') at the beginning; disabled when recursing.

    Returns
    -------
    str
        Title-cased string.

    """
    lines: list[str] = re.split("[\r\n]+", text)
    processed: list[str] = []
    for line in lines:
        all_caps: bool = line.upper() == line
        words: list[str] = re.split("[\t ]", line)
        tc_line: list[str | ImmutableBytes | ImmutableString] = []
        for word in words:
            if callback:
                new_word = callback(word, all_caps=all_caps)
                if new_word:
                    # Address #22: If a callback has done something
                    # specific, leave this string alone from now on
                    tc_line.append(_mark_immutable(new_word))
                    continue

            if all_caps:
                if UC_INITIALS.match(word):
                    tc_line.append(word)
                    continue

            if APOS_SECOND.match(word):
                if len(word[0]) == 1 and word[0] not in "aeiouAEIOU":
                    word = word[0].lower() + word[1] + word[2].upper() + word[3:]
                else:
                    word = word[0].upper() + word[1] + word[2].upper() + word[3:]
                tc_line.append(word)
                continue

            match = MAC_MC.match(word)
            if match:
                tc_line.append(
                    "%s%s"
                    % (
                        match.group(1).capitalize(),
                        titlecase(match.group(2), callback, True),
                    )
                )
                continue

            match = MR_MRS_MS_DR.match(word)
            if match:
                word = word[0].upper() + word[1:]
                tc_line.append(word)
                continue

            if INLINE_PERIOD.search(word) or (not all_caps and UC_ELSEWHERE.match(word)):
                tc_line.append(word)
                continue

            if SMALL_WORDS.match(word):
                tc_line.append(word.lower())
                continue

            if "/" in word and "//" not in word:
                slashed: map[str] = map(lambda t: titlecase(t, callback, False), word.split("/"))
                tc_line.append("/".join(slashed))
                continue

            if "-" in word:
                hyphenated: map[str] = map(lambda t: titlecase(t, callback, False), word.split("-"))
                tc_line.append("-".join(hyphenated))
                continue

            if all_caps:
                word = word.lower()

            # A term with all consonants should be considered an acronym.  But if it's
            # too short (like "St", don't apply this)
            if CONSONANTS.search(word) and len(word) > 2:
                tc_line.append(word.upper())
                continue

            # Just a normal word that needs to be capitalized
            tc_line.append(CAPFIRST.sub(lambda m: m.group(0).upper(), word))

        if small_first_last and tc_line:
            if not isinstance(tc_line[0], Immutable):
                tc_line[0] = SMALL_FIRST.sub(
                    lambda m: "%s%s" % (m.group(1), m.group(2).capitalize()), tc_line[0]
                )

            if not isinstance(tc_line[-1], Immutable):
                tc_line[-1] = SMALL_LAST.sub(lambda m: m.group(0).capitalize(), tc_line[-1])

        result: str = " ".join(tc_line)  # type: ignore[arg-type]

        result = SUBPHRASE.sub(lambda m: "%s%s" % (m.group(1), m.group(2).capitalize()), result)

        processed.append(result)

    result = "\n".join(processed)
    return result
