# -*- coding: utf-8 -*-
"""
Borrowed from GoSublime

Copyright (c) 2012 The GoSublime Authors

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from __future__ import annotations

import sublime

from ..diff_match_patch import diff_match_patch


class MergeException(Exception):
    """MergeException."""

    pass


def _merge_code(view: sublime.View, edit: sublime.Edit, original: str, modified: str) -> bool:
    """Merge code.

    Parameters
    ----------
    view : sublime.View
        A Sublime Text ``View`` object.
    edit : sublime.Edit
        A Sublime Text ``Edit`` object.
    original : str
        Original string.
    modified : str
        Modified string.

    Returns
    -------
    bool
        Is view dirty.

    Raises
    ------
    MergeException
        Error merging.
    """
    dmp: diff_match_patch = diff_match_patch()
    diffs: list[tuple[int, str]] = dmp.diff_main(original, modified)
    dmp.diff_cleanupEfficiency(diffs)
    i: int = 0
    dirty: bool = False

    for k, s in diffs:
        ln: int = len(s)

        if k == 0:
            # match
            ln = len(s)

            if view.substr(sublime.Region(i, i + ln)) != s:
                raise MergeException("mismatch", dirty)

            i += ln
        else:
            dirty = True

            if k > 0:
                # insert
                view.insert(edit, i, s)
                i += ln
            else:
                # delete
                if view.substr(sublime.Region(i, i + ln)) != s:
                    raise MergeException("mismatch", dirty)

                view.erase(edit, sublime.Region(i, i + ln))

    return dirty


def merge_code(
    view: sublime.View, edit: sublime.Edit, original: str, modified: str
) -> tuple[bool, str]:
    """Merge code.

    Parameters
    ----------
    view : sublime.View
        A Sublime Text ``View`` object.
    edit : sublime.Edit
        A Sublime Text ``Edit`` object.
    original : str
        Original string.
    modified : str
        Modified string.

    Returns
    -------
    tuple[bool, str]
        View state and error.
    """
    vs: sublime.Settings = view.settings()
    ttts: bool = vs.get("translate_tabs_to_spaces")

    if not original.strip():
        return (False, "")

    vs.set("translate_tabs_to_spaces", False)
    dirty: bool = False
    err: str = ""

    try:
        dirty = _merge_code(view, edit, original, modified)
    except MergeException as exc:
        dirty = True
        err = "Could not merge changes into the buffer, edit aborted: %s" % exc
        view.replace(edit, sublime.Region(0, view.size()), original)
    except Exception as ex:
        err = "Unknown exception: %s" % ex
    finally:
        vs.set("translate_tabs_to_spaces", ttts)
        return (dirty, err)
