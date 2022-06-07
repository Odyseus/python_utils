# -*- coding: utf-8 -*-
"""Configuration options.

Attributes
----------
BOLD_TEXT_STYLE_VALUES : tuple[str, ...]
    Values Google and others may use to indicate bold text.
RE_LINK : re.Pattern
    Compiled regular expression to match markdown styled links.
RE_MD_BACKSLASH_MATCHER : re.Pattern
    Compiled regular expression to match back-slashed characters.
RE_MD_CHARS_MATCHER : re.Pattern
    Compiled regular expression to match common characters used as Markdown markup.
RE_MD_CHARS_MATCHER_ALL : re.Pattern
    Compiled regular expression to match all characters used as Markdown markup.
RE_MD_DASH_MATCHER : re.Pattern
    Compiled regular expression to match dash styled unordered list items.
RE_MD_DOT_MATCHER : re.Pattern
    Compiled regular expression to match numbered styled ordered list items.
RE_MD_PLUS_MATCHER : re.Pattern
    Compiled regular expression to match plus styled unordered list items.
RE_ORDERED_LIST_MATCHER : re.Pattern
    Compiled regular expression to match ordered lists.
RE_SLASH_CHARS : str
    Regular expression to match characters that require escaping.
RE_SPACE : re.Pattern
    Compiled regular expression for checking space-only lines.
RE_UNORDERED_LIST_MATCHER : re.Pattern
    Compiled regular expression to match unordered lists.
TABLE_MARKER_FOR_PAD : str
    Marker to use for marking tables for padding post processing.
UNIFIABLE : dict[str, str]
    A dictionary which maps Unicode abbreviations to ASCII values.
VALID_OPTIONS : dict[str, ValidOptionsData]
    Configurable options. These options are attributes used by the HTML2Text class either by
    passing them as keyword arguments at instantiation time or through the
    :py:meth:`HTML2Text.set_options` method. These options are also used to auto-generate
    the CLI options (e.g. "body_width" will create the "--body-width" CLI option).
    Boolean options whose default values are ``True`` will be auto-negated (e.g.
    "inline_links" will create the "--no-inline-links" CLI option)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .._vendor.html2text import ValidOptionsData

import re


VALID_OPTIONS: dict[str, ValidOptionsData] = {
    "baseurl": {
        "typ": str,
        "doc": "Base URL for internal links ('a' and 'img' tags). It defaults to an empty string.",
        "default": "",
    },
    "body_width": {
        "typ": int,
        "doc": "Wrap long lines at position. It defaults to '0' (no wrapping).",
        "default": 0,
    },
    "bypass_tables": {
        "typ": bool,
        "doc": "Format tables in HTML rather than Markdown syntax.",
        "default": False,
    },
    "close_quote": {
        "typ": str,
        "doc": "Character used to close a quote when replacing the '<q>' tag. It defaults to '\"'.",
        "default": '"',
    },
    "default_image_alt": {
        "typ": str,
        "doc": "Default 'alt' attribute value for 'img' tags with missing 'alt' attributes. It defaults to an empty string.",
        "default": "",
    },
    "emphasis_mark": {
        "typ": str,
        "doc": "Character used when replacing the '<em>' tag. It defaults to '*'.",
        "default": "*",
    },
    "escape_snob": {
        "typ": bool,
        "doc": "Escape all special characters. Output is less readable, but avoids corner case formatting issues.",
        "default": False,
    },
    "google_doc": {
        "typ": bool,
        "doc": "If the input HTML should be treated as an HTML-exported Google Document.",
        "default": False,
    },
    "google_list_indent": {
        "typ": int,
        "doc": "Number of pixels to indent nested lists. Requires 'google_doc' option. It defaults to '36'.",
        "default": 36,
    },
    "hide_strikethrough": {
        "typ": bool,
        "doc": "Hide strike-through text. Requires 'google_doc' option.",
        "default": False,
    },
    "ignore_emphasis": {
        "typ": bool,
        "doc": "Whether to include formatting for emphasis ('em', 'i', 'u', 'strong', and 'b' tags).",
        "default": False,
    },
    "ignore_images": {
        "typ": bool,
        "doc": "Whether to ignore formatting for images ('img' tags).",
        "default": True,
    },
    "ignore_links": {
        "typ": bool,
        "doc": "Whether to ignore formatting for links ('a' tags).",
        "default": False,
    },
    "ignore_tables": {
        "typ": bool,
        "doc": "Ignore table-related tags ('table', 'th', 'td', 'tr') while keeping rows.",
        "default": False,
    },
    "images_as_html": {
        "typ": bool,
        "doc": "Always write 'img' tags as raw HTML; preserves 'height', 'width' and 'alt' if possible.",
        "default": False,
    },
    "images_to_alt": {
        "typ": bool,
        "doc": "Discard image data, only keep 'alt' attribute text.",
        "default": False,
    },
    "images_with_size": {
        "typ": bool,
        "doc": "Write 'img' tags with 'height' and 'width' attributes as raw HTML to retain dimensions.",
        "default": False,
    },
    "inline_links": {
        "typ": bool,
        "doc": "Whether to use inline links or reference style links formatting for images and links",
        "default": True,
    },
    "links_each_paragraph": {
        "typ": bool,
        "doc": "Put the links after each paragraph instead of at the end of the document.",
        "default": False,
    },
    "mark_code": {
        "typ": bool,
        "doc": "Wrap code blocks with triple back ticks.",
        "default": True,
    },
    "open_quote": {
        "typ": str,
        "doc": "Character used to open a quote when replacing the '<q>' tag. It defaults to '\"'.",
        "default": '"',
    },
    "pad_tables": {
        "typ": bool,
        "doc": "Pad the cells to equal column width in tables.",
        "default": True,
    },
    "protect_links": {
        "typ": bool,
        "doc": "Protect links from line breaks surrounding them with angle brackets (in addition to their square brackets).",
        "default": False,
    },
    "single_line_break": {
        "typ": bool,
        "doc": "Use a single line break after a block element rather than two line breaks. Requires 'body_width' setting to be 0.",
        "default": False,
    },
    "skip_internal_links": {
        "typ": bool,
        "doc": "Don't show internal links (href=\"#local-anchor\"). Corresponding link targets won't be visible in the plain text file anyway.",
        "default": True,
    },
    "strong_mark": {
        "typ": str,
        "doc": "Character used when replacing the '<strong>' tag. It defaults to '**'.",
        "default": "**",
    },
    "ul_item_mark": {
        "typ": str,
        "doc": "Unordered lists item mark.",
        "default": "-",
    },
    "unicode_snob": {
        "typ": bool,
        "doc": "Use Unicode characters instead of their ASCII pseudo-replacements.",
        "default": True,
    },
    "use_automatic_links": {
        "typ": bool,
        "doc": "Convert links with same 'href' and text to '<href>' format if they are absolute links.",
        "default": True,
    },
    "wrap_links": {
        "typ": bool,
        "doc": "Decide if links have to be wrapped during text wrapping (implies inline_links = False)",
        "default": False,
    },
    "wrap_list_items": {
        "typ": bool,
        "doc": "Wrap list items during conversion.",
        "default": False,
    },
}

# Internal options.

TABLE_MARKER_FOR_PAD: str = "special_marker_for_table_padding"
BOLD_TEXT_STYLE_VALUES: tuple[str, ...] = ("bold", "700", "800", "900")

RE_SPACE: re.Pattern = re.compile(r"\s\+")
RE_ORDERED_LIST_MATCHER: re.Pattern = re.compile(r"\d+\.\s")
RE_UNORDERED_LIST_MATCHER: re.Pattern = re.compile(r"[-\*\+]\s")
RE_MD_CHARS_MATCHER: re.Pattern = re.compile(r"([\\\[\]\(\)])")
RE_MD_CHARS_MATCHER_ALL: re.Pattern = re.compile(r"([`\*_{}\[\]\(\)#!])")
RE_LINK: re.Pattern = re.compile(r"(\[.*?\] ?\(.*?\))|(\[.*?\]:.*?)")
RE_MD_DOT_MATCHER: re.Pattern = re.compile(
    r"^(\s*\d+)(\.)(?=\s)",
    re.MULTILINE | re.VERBOSE,
)
RE_MD_PLUS_MATCHER: re.Pattern = re.compile(
    r"^(\s*)(\+)(?=\s)",
    flags=re.MULTILINE | re.VERBOSE,
)
RE_MD_DASH_MATCHER: re.Pattern = re.compile(
    r"^(\s*)(-)(?=\s|\-)",
    flags=re.MULTILINE | re.VERBOSE,
)
RE_SLASH_CHARS: str = r"\`*_{}[]()#+-.!"
RE_MD_BACKSLASH_MATCHER: re.Pattern = re.compile(
    r"(\\)(?=[%s])" % re.escape(RE_SLASH_CHARS),
    flags=re.VERBOSE,
)

UNIFIABLE: dict[str, str] = {
    "rsquo": "'",
    "lsquo": "'",
    "rdquo": '"',
    "ldquo": '"',
    "copy": "(C)",
    "mdash": "--",
    "nbsp": " ",
    "rarr": "->",
    "larr": "<-",
    "middot": "*",
    "ndash": "-",
    "oelig": "oe",
    "aelig": "ae",
    "agrave": "a",
    "aacute": "a",
    "acirc": "a",
    "atilde": "a",
    "auml": "a",
    "aring": "a",
    "egrave": "e",
    "eacute": "e",
    "ecirc": "e",
    "euml": "e",
    "igrave": "i",
    "iacute": "i",
    "icirc": "i",
    "iuml": "i",
    "ograve": "o",
    "oacute": "o",
    "ocirc": "o",
    "otilde": "o",
    "ouml": "o",
    "ugrave": "u",
    "uacute": "u",
    "ucirc": "u",
    "uuml": "u",
    "lrm": "",
    "rlm": "",
}
