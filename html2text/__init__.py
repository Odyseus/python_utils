# -*- coding: utf-8 -*-
"""Turn HTML into equivalent Markdown-structured text.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._vendor.html2text import OutCallback
    from collections.abc import Callable
    from types import TracebackType
    from typing import Any

import html.entities
import html.parser
import re
import urllib.parse as urlparse

from textwrap import wrap

from . import config
from .elements import AnchorElement
from .elements import ListElement

from .utils import dumb_css_parser
from .utils import element_style
from .utils import escape_md
from .utils import escape_md_section
from .utils import google_fixed_width_font
from .utils import google_has_height
from .utils import google_list_style
from .utils import google_text_emphasis
from .utils import hn
from .utils import list_numbering_start
from .utils import pad_tables_in_text
from .utils import skipwrap
from .utils import unifiable_n

__version__ = (2022, 6, 6)


# TODO:
# Support decoded entities with UNIFIABLE.


class HTML2Text(html.parser.HTMLParser):
    """Turn HTML into equivalent Markdown-structured text.

    Attributes
    ----------
    a : list[AnchorElement]
        Description
    abbr_data : str | None
        Last inner HTML (for ``abbr`` being defined).
    abbr_list : dict[str, str]
        Stack of abbreviations to write later.
    abbr_title : str | None
        Current abbreviation definition.
    absolute_url_matcher : re.Pattern
        Description
    acount : int
        Description
    astack : list[dict[str, str | None] | None]
        Description
    blockquote : int
        Description
    br_toggle : str
        Description
    code : bool
        Description
    current_tag : str
        Description
    drop_white_space : int
        Description
    emphasis : int
        Description
    empty_link : bool
        Description
    inheader : bool
        Description
    lastWasList : bool
        Description
    lastWasNL : bool
        Description
    list : list[ListElement]
        Description
    maybe_automatic_link : str | None
        Description
    out : Callable[[str], None] | OutCallback
        Description
    outcount : int
        Description
    outtextlist : list[str]
        List to store output characters before they are *joined*.
    p_p : int
        Number of newline characters to print before next output.
    pre : bool
        Description
    preceding_data : str
        Description
    preceding_stressed : bool
        Description
    quiet : int
        Description
    quote : bool
        Description
    space : bool
        Description
    split_next_td : bool
        Description
    start : bool
        Description
    startpre : bool
        Description
    stressed : bool
        Description
    style : int
        Description
    style_def : dict[str, dict[str, str]]
        Description
    table_start : bool
        Description
    tag_callback : Callable[[HTML2Text, str, dict[str, str | None], bool], str] | None
        Description
    tag_stack : list[tuple[str, dict[str, str | None], dict[str, str]]]
        Description
    td_count : int
        Description
    """

    def __init__(
        self,
        out: OutCallback | None = None,
        **kwargs: dict[str, str | bool | int],
    ) -> None:
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        out : OutCallback | None, optional
            Possible custom replacement for :py:meth:`HTML2Text.outtextf` (which appends lines of text).
        **kwargs : dict[str, str | bool | int]
            Keyword arguments. See :py:attr:`config.VALID_OPTIONS`.

        Raises
        ------
        TypeError
            Description
        """
        super().__init__(convert_charrefs=False)

        for opt_name, opt_def in config.VALID_OPTIONS.items():
            kw: Any = kwargs.get(opt_name)

            if kw is not None and not isinstance(kw, opt_def["typ"]):
                raise TypeError(
                    f"""'{opt_name}' option should be of type '{repr(opt_def["typ"])}'"""
                )

            setattr(self, opt_name, opt_def["default"] if kw is None else kw)

        self.split_next_td: bool = False
        self.td_count: int = 0
        self.table_start: bool = False
        self.tag_callback: Callable[
            [HTML2Text, str, dict[str, str | None], bool], str
        ] | None = None

        self.out: Callable[[str], None] | OutCallback = out if out is not None else self.outtextf
        self.outtextlist: list[str] = []
        self.quiet: int = 0
        self.p_p: int = 0
        self.outcount: int = 0
        self.start: bool = True
        self.space: bool = False
        self.a: list[AnchorElement] = []
        self.astack: list[dict[str, str | None] | None] = []
        self.maybe_automatic_link: str | None = None
        self.empty_link: bool = False
        self.absolute_url_matcher: re.Pattern = re.compile(r"^[a-zA-Z+]+://")
        self.acount: int = 0
        self.list: list[ListElement] = []
        self.blockquote: int = 0
        self.pre: bool = False
        self.startpre: bool = False
        self.code: bool = False
        self.quote: bool = False
        self.br_toggle: str = ""
        self.lastWasNL: bool = False
        self.lastWasList: bool = False
        self.style: int = 0
        self.style_def: dict[str, dict[str, str]] = {}
        self.tag_stack: list[tuple[str, dict[str, str | None], dict[str, str]]] = []
        self.emphasis: int = 0
        self.drop_white_space: int = 0
        self.inheader: bool = False
        self.abbr_title: str | None = None
        self.abbr_data: str | None = None
        self.abbr_list: dict[str, str] = {}
        self.stressed: bool = False
        self.preceding_stressed: bool = False
        self.preceding_data: str = ""
        self.current_tag: str = ""

        config.UNIFIABLE["nbsp"] = "&nbsp_place_holder;"

    def __getattr__(self, name: str) -> Any:
        """See :py:meth:`object.__getattr__`.

        This is here just to shut the hell up static type checkers.

        Parameters
        ----------
        name : str
            Attribute name.

        Raises
        ------
        AttributeError
            Not defined attribute.
        """
        raise AttributeError("Attribute %r not defined." % name)

    def __enter__(self) -> HTML2Text:
        """See :py:meth:`object.__enter__`.

        Returns
        -------
        HTML2Text
            Class instance.
        """
        return self

    def __exit__(self, exc_type: type, exc_value: BaseException, tb: TracebackType) -> None:
        """See :py:meth:`object.__exit__`.

        Parameters
        ----------
        exc_type : type
            Description
        exc_value : BaseException
            Description
        tb : TracebackType
            Description
        """
        self.outtextlist = []
        self.close()

    def set_options(self, **kwargs: dict[str, str | bool | int]) -> None:
        """Set options.

        Parameters
        ----------
        **kwargs : dict[str, str | bool | int]
            Keyword arguments. See :py:attr:`config.VALID_OPTIONS`.

        Raises
        ------
        KeyError
            If a passed option (keyword argument) isn't a valid option.
        TypeError
            If a passed option (keyword argument) is of the wrong type.
        """
        for k, v in kwargs.items():
            if k not in config.VALID_OPTIONS:
                raise KeyError(
                    f"""'{k}' option doesn't exist. '{repr(config.VALID_OPTIONS[k]["typ"])}'"""
                )

            if not isinstance(v, config.VALID_OPTIONS[k]["typ"]):
                raise TypeError(
                    f"""'{k}' option should be of type '{repr(config.VALID_OPTIONS[k]["typ"])}'"""
                )

            setattr(self, k, v)

    def feed(self, data: str) -> None:
        """Feed some text to the parser.

        Parameters
        ----------
        data : str
            Text to be parsed.
        """
        data = data.replace("</' + 'script>", "</ignore>")
        super().feed(data)

    def handle(self, data: str) -> str:
        """Main method to convert HTML into Markdown text.

        Parameters
        ----------
        data : str
            Text to be converted.

        Returns
        -------
        str
            Converted text.
        """
        self.feed(data)
        self.feed("")
        markdown = self.optwrap(self.finish())
        if self.pad_tables:
            return pad_tables_in_text(markdown)
        else:
            return markdown

    def outtextf(self, s: str) -> None:
        """Summary

        Parameters
        ----------
        s : str
            String to append to output storage list.
        """
        self.outtextlist.append(s)
        if s:
            self.lastWasNL = s[-1] == "\n"

    def finish(self) -> str:
        """Summary

        Returns
        -------
        str
            Description
        """
        self.close()

        self.pbr()
        self.o("", force="end")

        outtext: str = "".join(self.outtextlist)
        nbsp: str = html.entities.html5["nbsp;"] if self.unicode_snob else " "
        outtext = outtext.replace("&nbsp_place_holder;", nbsp)

        # Clear self.outtextlist to avoid memory leak of its content to the next handling.
        self.outtextlist = []
        self.reset()

        return outtext

    def handle_charref(self, c: str) -> None:
        """See :py:meth:`HTMLParser.handle_charref`.

        Parameters
        ----------
        c : str
            Description
        """
        self.handle_data(self.charref(c), True)

    def handle_entityref(self, c: str) -> None:
        """See :py:meth:`HTMLParser.handle_entityref`.

        Parameters
        ----------
        c : str
            Description
        """
        ref: str = self.entityref(c)

        # ref may be an empty string (e.g. for &lrm;/&rlm; markers that should
        # not contribute to the final output).
        # self.handle_data cannot handle a zero-length string right after a
        # stressed tag or mid-text within a stressed tag (text get split and
        # self.stressed/self.preceding_stressed gets switched after the first
        # part of that text).
        if ref:
            self.handle_data(ref, True)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """See :py:meth:`HTMLParser.handle_starttag`.

        Parameters
        ----------
        tag : str
            Description
        attrs : list[tuple[str, str | None]]
            Description
        """
        self.handle_tag(tag, dict(attrs), start=True)

    def handle_endtag(self, tag: str) -> None:
        """See :py:meth:`HTMLParser.handle_endtag`.

        Parameters
        ----------
        tag : str
            Description
        """
        self.handle_tag(tag, {}, start=False)

    def previousIndex(self, attrs: dict[str, str | None]) -> int | None:
        """Previous index.

        Parameters
        ----------
        attrs : dict[str, str | None]
            Description

        Returns
        -------
        int | None
            The index of certain set of attributes (of a link) in the self.a list.
            If the set of attributes is not found, returns :py:class:`None`.
        """
        if "href" not in attrs:
            return None

        match: bool = False
        for i, a in enumerate(self.a):
            if "href" in a.attrs and a.attrs["href"] == attrs["href"]:
                if "title" in a.attrs or "title" in attrs:
                    if (
                        "title" in a.attrs
                        and "title" in attrs
                        and a.attrs["title"] == attrs["title"]
                    ):
                        match = True
                else:
                    match = True

            if match:
                return i
        return None

    def handle_emphasis(
        self, start: bool, tag_style: dict[str, str], parent_style: dict[str, str]
    ) -> None:
        """Handles various text emphases.

        Parameters
        ----------
        start : bool
            Description
        tag_style : dict[str, str]
            Description
        parent_style : dict[str, str]
            Description
        """
        tag_emphasis: list[str] = google_text_emphasis(tag_style)
        parent_emphasis: list[str] = google_text_emphasis(parent_style)

        # handle Google's text emphasis
        strikethrough: bool = "line-through" in tag_emphasis and self.hide_strikethrough

        # google and others may mark a font's weight as `bold` or `700`
        bold: bool = False
        for bold_marker in config.BOLD_TEXT_STYLE_VALUES:
            bold = bold_marker in tag_emphasis and bold_marker not in parent_emphasis
            if bold:
                break

        italic: bool = "italic" in tag_emphasis and "italic" not in parent_emphasis
        fixed: bool = (
            google_fixed_width_font(tag_style)
            and not google_fixed_width_font(parent_style)
            and not self.pre
        )

        if start:
            # crossed-out text must be handled before other attributes
            # in order not to output qualifiers unnecessarily
            if bold or italic or fixed:
                self.emphasis += 1
            if strikethrough:
                self.quiet += 1
            if italic:
                self.o(self.emphasis_mark)
                self.drop_white_space += 1
            if bold:
                self.o(self.strong_mark)
                self.drop_white_space += 1
            if fixed:
                self.o("`")
                self.drop_white_space += 1
                self.code = True
        else:
            if bold or italic or fixed:
                # there must not be whitespace before closing emphasis mark
                self.emphasis -= 1
                self.space = False
            if fixed:
                if self.drop_white_space:
                    # empty emphasis, drop it
                    self.drop_white_space -= 1
                else:
                    self.o("`")
                self.code = False
            if bold:
                if self.drop_white_space:
                    # empty emphasis, drop it
                    self.drop_white_space -= 1
                else:
                    self.o(self.strong_mark)
            if italic:
                if self.drop_white_space:
                    # empty emphasis, drop it
                    self.drop_white_space -= 1
                else:
                    self.o(self.emphasis_mark)
            # space is only allowed after *all* emphasis marks
            if (bold or italic) and not self.emphasis:
                self.o(" ")
            if strikethrough:
                self.quiet -= 1

    def handle_tag(self, tag: str, attrs: dict[str, str | None], start: bool) -> None:
        """Handle various HTML tags.

        Parameters
        ----------
        tag : str
            Description
        attrs : dict[str, str | None]
            Description
        start : bool
            Description

        Returns
        -------
        None
            Description
        """
        self.current_tag = tag

        if self.tag_callback is not None:
            if self.tag_callback(self, tag, attrs, start) is True:
                return

        # first thing inside the anchor tag is another tag
        # that produces some output
        if (
            start
            and self.maybe_automatic_link is not None
            and tag not in ["p", "div", "style", "dl", "dt"]
            and (tag != "img" or self.ignore_images)
        ):
            self.o("[")
            self.maybe_automatic_link = None
            self.empty_link = False

        if self.google_doc:
            # the attrs parameter is empty for a closing tag. in addition, we
            # need the attributes of the parent nodes in order to get a
            # complete style description for the current element. we assume
            # that google docs export well formed html.
            parent_style: dict[str, str] = {}
            tag_style: dict = {}
            if start:
                if self.tag_stack:
                    parent_style = self.tag_stack[-1][2]
                tag_style = element_style(attrs, self.style_def, parent_style)
                self.tag_stack.append((tag, attrs, tag_style))
            else:
                dummy, attrs, tag_style = self.tag_stack.pop() if self.tag_stack else (None, {}, {})
                if self.tag_stack:
                    parent_style = self.tag_stack[-1][2]

        if hn(tag):
            self.p()
            if start:
                self.inheader = True
                self.o(hn(tag) * "#" + " ")
            else:
                self.inheader = False
                return  # prevent redundant emphasis marks on headers

        if tag in ["p", "div"]:
            if self.google_doc:
                if start and google_has_height(tag_style):
                    self.p()
                else:
                    self.soft_br()
            elif self.astack and tag == "div":
                pass
            else:
                self.p()

        if tag == "br" and start:
            if self.blockquote > 0:
                self.o("  \n> ")
            else:
                self.o("  \n")

        if tag == "hr" and start:
            self.p()
            self.o("* * *")
            self.p()

        if tag in ["head", "style", "script"]:
            if start:
                self.quiet += 1
            else:
                self.quiet -= 1

        if tag == "style":
            if start:
                self.style += 1
            else:
                self.style -= 1

        if tag in ["body"]:
            self.quiet = 0  # sites like 9rules.com never close <head>

        if tag == "blockquote":
            if start:
                self.p()
                self.o("> ", force=True)
                self.start = True
                self.blockquote += 1
            else:
                self.blockquote -= 1
                self.p()

        def no_preceding_space(self: HTML2Text) -> bool:
            """Summary

            Returns
            -------
            bool
                Description
            """
            return bool(self.preceding_data and re.match(r"[^\s]", self.preceding_data[-1]))

        if tag in ["em", "i", "u"] and not self.ignore_emphasis:
            if start and no_preceding_space(self):
                emphasis = " " + self.emphasis_mark
            else:
                emphasis = self.emphasis_mark

            self.o(emphasis)
            if start:
                self.stressed = True

        if tag in ["strong", "b"] and not self.ignore_emphasis:
            if start and no_preceding_space(self):
                strong = " " + self.strong_mark
            else:
                strong = self.strong_mark

            self.o(strong)
            if start:
                self.stressed = True

        if tag in ["del", "strike", "s"]:
            if start and no_preceding_space(self):
                strike = " ~~"
            else:
                strike = "~~"

            self.o(strike)
            if start:
                self.stressed = True

        if self.google_doc:
            if not self.inheader:
                # handle some font attributes, but leave headers clean
                self.handle_emphasis(start, tag_style, parent_style)

        if tag in ["kbd", "code", "tt"] and not self.pre:
            self.o("`")  # TODO: `` `this` ``
            self.code = not self.code

        if tag == "abbr":
            if start:
                self.abbr_title = None
                self.abbr_data = ""
                if "title" in attrs:
                    self.abbr_title = attrs["title"]
            else:
                if self.abbr_title is not None:
                    assert self.abbr_data is not None
                    self.abbr_list[self.abbr_data] = self.abbr_title
                    self.abbr_title = None
                self.abbr_data = None

        if tag == "q":
            if not self.quote:
                self.o(self.open_quote)
            else:
                self.o(self.close_quote)
            self.quote = not self.quote

        def link_url(self: HTML2Text, link: str, title: str = "") -> None:
            """Summary

            Parameters
            ----------
            link : str
                Description
            title : str, optional
                Description
            """
            url = urlparse.urljoin(self.baseurl, link)
            title = ' "{}"'.format(title) if title.strip() else ""
            self.o("]({url}{title})".format(url=escape_md(url), title=title))

        if tag == "a" and not self.ignore_links:
            if start:
                if (
                    "href" in attrs
                    and attrs["href"] is not None
                    and not (self.skip_internal_links and attrs["href"].startswith("#"))
                ):
                    self.astack.append(attrs)
                    self.maybe_automatic_link = attrs["href"]
                    self.empty_link = True
                    if self.protect_links:
                        attrs["href"] = "<" + attrs["href"] + ">"
                else:
                    self.astack.append(None)
            else:
                if self.astack:
                    a = self.astack.pop()
                    if self.maybe_automatic_link and not self.empty_link:
                        self.maybe_automatic_link = None
                    elif a:
                        assert a["href"] is not None
                        if self.empty_link:
                            self.o("[")
                            self.empty_link = False
                            self.maybe_automatic_link = None
                        if self.inline_links:
                            title = a.get("title") or ""
                            title = escape_md(title)
                            link_url(self, a["href"], title)
                        else:
                            i = self.previousIndex(a)
                            if i is not None:
                                a_props = self.a[i]
                            else:
                                self.acount += 1
                                a_props = AnchorElement(a, self.acount, self.outcount)
                                self.a.append(a_props)
                            self.o("][" + str(a_props.count) + "]")

        if tag == "img" and start and not self.ignore_images:
            if "src" in attrs:
                assert attrs["src"] is not None
                if not self.images_to_alt:
                    attrs["href"] = attrs["src"]
                alt = attrs.get("alt") or self.default_image_alt

                # If we have images_with_size, write raw html including width,
                # height, and alt attributes
                if self.images_as_html or (
                    self.images_with_size and ("width" in attrs or "height" in attrs)
                ):
                    self.o("<img src='" + attrs["src"] + "' ")
                    if "width" in attrs:
                        assert attrs["width"] is not None
                        self.o("width='" + attrs["width"] + "' ")
                    if "height" in attrs:
                        assert attrs["height"] is not None
                        self.o("height='" + attrs["height"] + "' ")
                    if alt:
                        self.o("alt='" + alt + "' ")
                    self.o("/>")
                    return

                # If we have a link to create, output the start
                if self.maybe_automatic_link is not None:
                    href = self.maybe_automatic_link
                    if (
                        self.images_to_alt
                        and escape_md(alt) == href
                        and self.absolute_url_matcher.match(href)
                    ):
                        self.o("<" + escape_md(alt) + ">")
                        self.empty_link = False
                        return
                    else:
                        self.o("[")
                        self.maybe_automatic_link = None
                        self.empty_link = False

                # If we have images_to_alt, we discard the image itself,
                # considering only the alt text.
                if self.images_to_alt:
                    self.o(escape_md(alt))
                else:
                    self.o("![" + escape_md(alt) + "]")
                    if self.inline_links:
                        href = attrs.get("href") or ""
                        self.o("(" + escape_md(urlparse.urljoin(self.baseurl, href)) + ")")
                    else:
                        i = self.previousIndex(attrs)
                        if i is not None:
                            a_props = self.a[i]
                        else:
                            self.acount += 1
                            a_props = AnchorElement(attrs, self.acount, self.outcount)
                            self.a.append(a_props)
                        self.o("[" + str(a_props.count) + "]")

        if tag == "dl" and start:
            self.p()
        if tag == "dt" and not start:
            self.pbr()
        if tag == "dd" and start:
            self.o("    ")
        if tag == "dd" and not start:
            self.pbr()

        if tag in ["ol", "ul"]:
            # Google Docs create sub lists as top level lists
            if not self.list and not self.lastWasList:
                self.p()
            if start:
                if self.google_doc:
                    list_style = google_list_style(tag_style)
                else:
                    list_style = tag
                numbering_start = list_numbering_start(attrs)
                self.list.append(ListElement(list_style, numbering_start))
            else:
                if self.list:
                    self.list.pop()
                    if not self.google_doc and not self.list:
                        self.o("\n")
            self.lastWasList = True
        else:
            self.lastWasList = False

        if tag == "li":
            self.pbr()
            if start:
                if self.list:
                    li = self.list[-1]
                else:
                    li = ListElement("ul", 0)
                if self.google_doc:
                    nest_count = self.google_nest_count(tag_style)
                else:
                    nest_count = len(self.list)
                # TODO: line up <ol><li>s > 9 correctly.
                if nest_count == 1:
                    self.o("")
                else:
                    self.o("    " * (nest_count - 1))

                if li.name == "ul":
                    self.o(self.ul_item_mark + " ")
                elif li.name == "ol":
                    li.num += 1
                    self.o(str(li.num) + ". ")
                self.start = True

        if tag in ["table", "tr", "td", "th"]:
            if self.ignore_tables:
                if tag == "tr":
                    if start:
                        pass
                    else:
                        self.soft_br()
                else:
                    pass

            elif self.bypass_tables:
                if start:
                    self.soft_br()
                if tag in ["td", "th"]:
                    if start:
                        self.o("<{}>\n\n".format(tag))
                    else:
                        self.o("\n</{}>".format(tag))
                else:
                    if start:
                        self.o("<{}>".format(tag))
                    else:
                        self.o("</{}>".format(tag))

            else:
                if tag == "table":
                    if start:
                        self.table_start = True
                        if self.pad_tables:
                            self.o("<" + config.TABLE_MARKER_FOR_PAD + ">")
                            self.o("  \n")
                    else:
                        if self.pad_tables:
                            self.o("</" + config.TABLE_MARKER_FOR_PAD + ">")
                            self.o("  \n")
                if tag in ["td", "th"] and start:
                    if self.split_next_td:
                        self.o("| ")
                    self.split_next_td = True

                if tag == "tr" and start:
                    self.td_count = 0
                if tag == "tr" and not start:
                    self.split_next_td = False
                    self.soft_br()
                if tag == "tr" and not start and self.table_start:
                    # Underline table header
                    self.o("|".join(["---"] * self.td_count))
                    self.soft_br()
                    self.table_start = False
                if tag in ["td", "th"] and start:
                    self.td_count += 1

        if tag == "pre":
            if start:
                self.startpre = True
                self.pre = True
            else:
                self.pre = False
                if self.mark_code:
                    self.out("\n```")
            self.p()

    def pbr(self) -> None:
        """Pretty print has a line break."""
        if self.p_p == 0:
            self.p_p = 1

    def p(self) -> None:
        """Set pretty print to 1 or 2 lines."""
        self.p_p = 1 if self.single_line_break else 2

    def soft_br(self) -> None:
        """Soft breaks."""
        self.pbr()
        self.br_toggle = "  "

    def o(self, data: str, puredata: bool = False, force: bool | str = False) -> None:
        """Deal with indentation and whitespace.

        Parameters
        ----------
        data : str
            Description
        puredata : bool, optional
            Description
        force : bool | str, optional
            Description

        Returns
        -------
        None
            Description
        """
        if self.abbr_data is not None:
            self.abbr_data += data

        if not self.quiet:
            if self.google_doc:
                # prevent white space immediately after 'begin emphasis'
                # marks ('**' and '_')
                lstripped_data = data.lstrip()
                if self.drop_white_space and not (self.pre or self.code):
                    data = lstripped_data
                if lstripped_data != "":
                    self.drop_white_space = 0

            if puredata and not self.pre:
                # This is a very dangerous call ... it could mess up
                # all handling of &nbsp; when not handled properly
                # (see entityref)
                data = re.sub(r"\s+", r" ", data)
                if data and data[0] == " ":
                    self.space = True
                    data = data[1:]
            if not data and not force:
                return

            if self.startpre:
                # self.out(" :") #TODO: not output when already one there
                if not data.startswith("\n") and not data.startswith("\r\n"):
                    # <pre>stuff...
                    data = "\n" + data
                if self.mark_code:
                    self.out("\n\n```\n")
                    self.p_p = 0

            bq = ">" * self.blockquote
            if not (force and data and data[0] == ">") and self.blockquote:
                bq += " "

            if self.pre:
                if not self.list and not self.mark_code:
                    bq += "    "
                # else: list content is already partially indented
                bq += "    " * len(self.list)

                data = data.replace("\n", "\n" + bq)

            if self.startpre:
                self.startpre = False
                if self.list:
                    # use existing initial indentation
                    data = data.lstrip("\n")

            if self.start:
                self.space = False
                self.p_p = 0
                self.start = False

            if force == "end":
                # It's the end.
                self.p_p = 0
                self.out("\n")
                self.space = False

            if self.p_p:
                self.out((self.br_toggle + "\n" + bq) * self.p_p)
                self.space = False
                self.br_toggle = ""

            if self.space:
                if not self.lastWasNL:
                    self.out(" ")
                self.space = False

            if self.a and ((self.p_p == 2 and self.links_each_paragraph) or force == "end"):
                if force == "end":
                    self.out("\n")

                newa = []
                for link in self.a:
                    if self.outcount > link.outcount:
                        self.out(
                            "   ["
                            + str(link.count)
                            + "]: "
                            + urlparse.urljoin(self.baseurl, link.attrs["href"])
                        )
                        if "title" in link.attrs:
                            assert link.attrs["title"] is not None
                            self.out(" (" + link.attrs["title"] + ")")
                        self.out("\n")
                    else:
                        newa.append(link)

                # Don't need an extra line when nothing was done.
                if self.a != newa:
                    self.out("\n")

                self.a = newa

            if self.abbr_list and force == "end":
                for abbr, definition in self.abbr_list.items():
                    self.out("  *[" + abbr + "]: " + definition + "\n")

            self.p_p = 0
            self.out(data)
            self.outcount += 1

    def handle_data(self, data: str, entity_char: bool = False) -> None:
        """Summary

        Parameters
        ----------
        data : str
            Description
        entity_char : bool, optional
            Description

        Returns
        -------
        None
            Description
        """
        if not data:
            # Data may be empty for some HTML entities. For example,
            # LEFT-TO-RIGHT MARK.
            return

        if self.stressed:
            data = data.strip()
            self.stressed = False
            self.preceding_stressed = True
        elif self.preceding_stressed:
            if (
                re.match(r"[^\s.!?]", data[0])
                and not hn(self.current_tag)
                and self.current_tag not in ["a", "code", "pre"]
            ):
                # should match a letter or common punctuation
                data = " " + data
            self.preceding_stressed = False

        if self.style:
            self.style_def.update(dumb_css_parser(data))

        if self.maybe_automatic_link is not None:
            href = self.maybe_automatic_link
            if href == data and self.absolute_url_matcher.match(href) and self.use_automatic_links:
                self.o("<" + data + ">")
                self.empty_link = False
                return
            else:
                self.o("[")
                self.maybe_automatic_link = None
                self.empty_link = False

        if not self.code and not self.pre and not entity_char:
            data = escape_md_section(data, snob=self.escape_snob)
        self.preceding_data = data
        self.o(data, puredata=True)

    def charref(self, name: str) -> str:
        """Summary

        Parameters
        ----------
        name : str
            Description

        Returns
        -------
        str
            Description
        """
        c: int = int(name[1:], 16) if name[0] in ["x", "X"] else int(name)

        if not self.unicode_snob and c in unifiable_n:
            return unifiable_n[c]
        else:
            try:
                return chr(c)
            except ValueError:  # invalid unicode
                return ""

    def entityref(self, c: str) -> str:
        """Summary

        Parameters
        ----------
        c : str
            Description

        Returns
        -------
        str
            Description
        """
        if not self.unicode_snob and c in config.UNIFIABLE:
            return config.UNIFIABLE[c]
        try:
            ch = html.entities.html5[c + ";"]
        except KeyError:
            return "&" + c + ";"
        return config.UNIFIABLE[c] if c == "nbsp" else ch

    def google_nest_count(self, style: dict[str, str]) -> int:
        """Calculate the nesting count of Google doc lists.

        Parameters
        ----------
        style : dict[str, str]
            Description

        Returns
        -------
        int
            Description
        """
        nest_count: int = 0
        if "margin-left" in style:
            nest_count = int(style["margin-left"][:-2]) // self.google_list_indent

        return nest_count

    def optwrap(self, text: str) -> str:
        """Wrap all paragraphs in the provided text.

        Parameters
        ----------
        text : str
            Description

        Returns
        -------
        str
            Description
        """
        if not self.body_width:
            return text

        result: str = ""
        newlines: int = 0
        # I cannot think of a better solution for now.
        # To avoid the non-wrap behaviour for entire paras
        # because of the presence of a link in it
        if not self.wrap_links:
            self.inline_links = False
        for para in text.split("\n"):
            if len(para) > 0:
                if not skipwrap(para, self.wrap_links, self.wrap_list_items):
                    indent = ""
                    if para.startswith("    " + self.ul_item_mark):
                        # list item continuation: add a double indent to the
                        # new lines
                        indent = "        "
                    elif para.startswith("> "):
                        # blockquote continuation: add the greater than symbol
                        # to the new lines
                        indent = "> "
                    wrapped: list[str] = wrap(
                        para,
                        self.body_width,
                        break_long_words=False,
                        subsequent_indent=indent,
                    )
                    result += "\n".join(wrapped)
                    if para.endswith("  "):
                        result += "  \n"
                        newlines = 1
                    elif indent:
                        result += "\n"
                        newlines = 1
                    else:
                        result += "\n\n"
                        newlines = 2
                else:
                    # Warning for the tempted!!!
                    # Be aware that obvious replacement of this with
                    # line.isspace()
                    # DOES NOT work! Explanations are welcome.
                    if not config.RE_SPACE.match(para):
                        result += para + "\n"
                        newlines = 1
            else:
                if newlines < 2:
                    result += "\n"
                    newlines += 1
        return result


def html2text(html: str, **kwargs) -> str:
    """Turn HTML into equivalent Markdown-structured text.

    Parameters
    ----------
    html : str
        HTML to convert.
    **kwargs : dict[str, Union[str, bool, int]]
        Keyword arguments. See :py:attr:`config.VALID_OPTIONS`.

    Returns
    -------
    str
        Converted Markdown text.
    """
    h = HTML2Text(**kwargs)

    return h.handle(html)
