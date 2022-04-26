# -*- coding: utf-8 -*-
"""Programmatic completions utilities.

Note
....
I would write a trillion lines of Python just to avoid writing one line of JSON. LOL
"""
import html

import sublime

_completions_settings_keys = (
    ("completions", []),
    ("completions_user", []),
    ("completions_scope", ""),
    ("inhibit_word_completions", False),
    ("inhibit_explicit_completions", False),
    ("dynamic_completions", False),
    ("inhibit_reorder", False),
)


_kind_map = {
    "ambiguous": sublime.KIND_AMBIGUOUS,
    "function": sublime.KIND_FUNCTION,
    "keyword": sublime.KIND_KEYWORD,
    "markup": sublime.KIND_MARKUP,
    "namespace": sublime.KIND_NAMESPACE,
    "navigation": sublime.KIND_NAVIGATION,
    "snippet": sublime.KIND_SNIPPET,
    "type": sublime.KIND_TYPE,
    "variable": sublime.KIND_VARIABLE,
}


_kind_id_map = {
    "ambiguous": sublime.KIND_ID_AMBIGUOUS,
    "function": sublime.KIND_ID_FUNCTION,
    "keyword": sublime.KIND_ID_KEYWORD,
    "markup": sublime.KIND_ID_MARKUP,
    "namespace": sublime.KIND_ID_NAMESPACE,
    "navigation": sublime.KIND_ID_NAVIGATION,
    "snippet": sublime.KIND_ID_SNIPPET,
    "type": sublime.KIND_ID_TYPE,
    "variable": sublime.KIND_ID_VARIABLE,
}


def get_kind_tuple(k):
    """Get kind :py:class:`tuple`.

    Convert a kind list as defined in a completions file (``["function", "m", "Method"]``)
    into a kind that can be used in a ``sublime.CompletionItem`` element
    (``(sublime.KIND_ID_FUNCTION, "m", "Method")``).

    Parameters
    ----------
    k : list
        A kind list in the form ``["function", "m", "Method"]``.

    Returns
    -------
    tuple
        A kind :py:class:`tuple`.
    """
    return (_kind_id_map.get(k[0]), k[1], k[2])


def create_completions_list(
    settings,
    kind=sublime.KIND_AMBIGUOUS,
    completion_format=sublime.COMPLETION_FORMAT_SNIPPET,
    details_template=None,
    logger=None,
):
    """Create completions list.

    Parameters
    ----------
    settings : settings.SettingsManager
        The settings object from which to get the completions settings from.
    kind : TYPE, optional
        A kind used in case an item in the completions definitions do not specify one.
    completion_format : int, optional
        The format of the completion.
    details_template : None, optional
        Description
    logger : SublimeLogger
        The logger.
    """
    completions_settings = {}
    try:
        for key, default_value in _completions_settings_keys:
            val = settings.get(key, default_value)
            completions_settings[key] = val
    except Exception as err:
        sublime.status_message("Error updating completions")
        logger.error(err)

    try:
        completions_items = []

        for c in (
            completions_settings["completions"]
            + completions_settings["completions_user"]
        ):
            item_args = {
                "trigger": c["trigger"],
                "completion": c["contents"],
            }
            k = c.get("kind")

            if isinstance(k, str):
                item_args["kind"] = _kind_map.get(k, kind)
            elif isinstance(k, list):
                item_args["kind"] = get_kind_tuple(k)
            else:
                item_args["kind"] = kind

            item_args["completion_format"] = (
                c.get("completion_format") or completion_format
            )
            item_args["details"] = c.get("details") or (
                details_template.format(html.escape(c["contents"]))
                if details_template
                else ""
            )

            if c.get("annotation"):
                item_args["annotation"] = c.get("annotation")

            completions_items.append(sublime.CompletionItem(**item_args))

        ody_all_completions = sublime.CompletionList(
            completions_items,
            completions_settings["inhibit_word_completions"]
            * sublime.INHIBIT_WORD_COMPLETIONS
            | completions_settings["inhibit_explicit_completions"]
            * sublime.INHIBIT_EXPLICIT_COMPLETIONS
            | completions_settings["dynamic_completions"] * sublime.DYNAMIC_COMPLETIONS
            | completions_settings["inhibit_reorder"] * sublime.INHIBIT_REORDER,
        )
    except KeyError:
        sublime.status_message("Error updating completions")
        ody_all_completions = []
        logger.error(
            "Completions must be a list of dictionaries with at least two keys ('trigger' and 'contents')."
        )
    except BaseException as err:
        sublime.status_message("Error updating completions")
        ody_all_completions = []
        logger.error(err)

    return ody_all_completions


if __name__ == "__main__":
    pass
