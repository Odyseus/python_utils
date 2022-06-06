# -*- coding: utf-8 -*-
"""Various constants.

Attributes
----------
ALPHA_NUMERIC
    Compiled regular expression used to clean up non-alpha-numeric characters from a color name.
FLOAT_ERROR
    Soften inequalities and some rounding issue based on float.
LONG_HEX_COLOR
    Compiled regular expression to match long `HEX <https://en.wikipedia.org/wiki/Web_colors>`__ colors.
SHORT_HEX_COLOR
    Compiled regular expression to match short `HEX <https://en.wikipedia.org/wiki/Web_colors>`__ colors.
SHORT_OR_LONG_HEX_COLOR : re.Pattern
    Compiled regular expression to match short or long `HEX <https://en.wikipedia.org/wiki/Web_colors>`__ colors.
"""
from __future__ import annotations

import re

FLOAT_ERROR: float = 0.0000005
LONG_HEX_COLOR: re.Pattern = re.compile(r"^#[0-9a-fA-F]{6}$")
SHORT_HEX_COLOR: re.Pattern = re.compile(r"^#[0-9a-fA-F]{3}$")
SHORT_OR_LONG_HEX_COLOR: re.Pattern = re.compile(r"^#[0-9a-fA-F]{3}([0-9a-fA-F]{3})?$")
ALPHA_NUMERIC: re.Pattern = re.compile(r"[^a-zA-Z0-9]")
