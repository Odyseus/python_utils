# -*- coding: utf-8 -*-
"""Programmatic completions utilities.

Note
....
I would write a trillion lines of Python just to avoid writing one line of JSON. LOL
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from python_utils import logging_system
    from python_utils.sublime_text_utils.settings import SettingsManager

import html

import sublime

_completions_settings_keys: tuple = (
    ("completions", []),
    ("completions_user", []),
    ("completions_scope", ""),
    ("inhibit_word_completions", False),
    ("inhibit_explicit_completions", False),
    ("dynamic_completions", False),
    ("inhibit_reorder", False),
)


def get_kind(kind_name: str, t: str = "tuple") -> int | tuple[int, str, str]:
    """Get kind ID or tuple based on a kind name.

    Parameters
    ----------
    kind_name : str
        A kind name.
    t : str, optional
        One of **tuple** or **id**.

    Returns
    -------
    int | tuple[int, str, str]
        A kind ID or tuple.
    """
    fallback_attr = "KIND_ID_AMBIGUOUS" if t == "id" else "KIND_AMBIGUOUS"
    attr = "KIND_" + ("ID_" if t == "id" else "") + kind_name.upper()

    return getattr(sublime, attr, getattr(sublime, fallback_attr))


def create_completions_list(
    settings: SettingsManager,
    settings_prefix: str = "",
    kind: str | list[str] = sublime.KIND_AMBIGUOUS,
    completion_format: int = sublime.COMPLETION_FORMAT_SNIPPET,
    details_template: str | None = None,
    logger: logging_system.Logger = None,
) -> sublime.CompletionList | list:
    """Create completions list.

    Parameters
    ----------
    settings : SettingsManager
        The settings object from which to get the completions settings from.
    settings_prefix : str, optional
        The name of a settings could be prefixed. Instead of ``completions``, a setting could be
        named ``plugin_name.completions``, with ``plugin_name.`` being the prefix.
    kind : str | list[str], optional
        A kind used in case an item in the completions definitions do not specify one.
    completion_format : int, optional
        The format of the completion.
    details_template : str | None, optional
        An HTML string that can be used as template for the ``details`` parameter of a
        ``sublime.CompletionItem`` item. :py:meth:`format` will be called on the string
        with the value of the ``contents`` key of a completion definition.
    logger : logging_system.Logger, optional
        The logger.

    Returns
    -------
    sublime.CompletionList | list
        A list of completions that can be handled by the ``on_query_completions`` method. of a
        ``sublime_plugin.EventListener`` or ``sublime_plugin.ViewEventListener`` class.
    """
    completions_settings: dict = {}
    try:
        for key, default_value in _completions_settings_keys:
            val = settings.get(settings_prefix + key, default_value)
            completions_settings[key] = val
    except Exception as err:
        sublime.status_message("Error updating completions")
        logger.error(err)

    ody_all_completions: sublime.CompletionList | list = []
    completions_items: list[sublime.CompletionItem] = []

    try:
        for c in completions_settings["completions"] + completions_settings["completions_user"]:
            item_args: dict = {
                "trigger": c["trigger"],
                "completion": c["contents"],
            }
            k: str | list[str] = c.get("kind")

            if isinstance(k, str):
                item_args["kind"] = get_kind(k, t="tuple")
            elif isinstance(k, list):
                item_args["kind"] = (get_kind(k[0], t="id"), k[1], k[2])
            else:
                item_args["kind"] = kind

            item_args["completion_format"] = c.get("completion_format") or completion_format
            item_args["details"] = c.get("details") or (
                details_template.format(html.escape(c["contents"])) if details_template else ""
            )

            if c.get("annotation"):
                item_args["annotation"] = c.get("annotation")

            completions_items.append(sublime.CompletionItem(**item_args))

        ody_all_completions = sublime.CompletionList(
            completions_items,
            completions_settings["inhibit_word_completions"] * sublime.INHIBIT_WORD_COMPLETIONS
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
