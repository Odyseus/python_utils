# -*- coding: utf-8 -*-
"""Various utilities.
"""
import os
import sys

from collections import ChainMap
from collections.abc import Mapping
from collections.abc import Sequence

import sublime
import sublime_plugin

from .. import cmd_utils


def is_editable_view(view):
    return all(
        (
            view and not view.element(),
            view and not view.is_scratch(),
            view and not view.is_read_only(),
            view and not view.is_loading(),
        )
    )


def has_right_syntax(view, view_syntaxes=[], strict=False):
    """Has right syntax.

    Check if the view is of the desired syntax listed in ``view_syntaxes``.

    Parameters
    ----------
    view : sublime.View
        A Sublime Text ``View`` object.
    view_syntaxes : list, string, optional
        List of syntaxes to check against.
    strict : bool, optional
        Perform equality checks instead of membership checks.

    Returns
    -------
    bool
        If the view has the right syntax.
    """
    syntax = view.settings().get("syntax").split("/")[-1].lower()

    if isinstance(view_syntaxes, list):
        return any(
            [
                (s.lower() == syntax if strict else s.lower() in syntax)
                for s in view_syntaxes
            ]
        )
    elif isinstance(view_syntaxes, str):
        return (
            view_syntaxes.lower() == syntax
            if strict
            else view_syntaxes.lower() in syntax
        )

    return False


def has_right_extension(view, file_extensions=[]):
    """Has the right file extension.

    Parameters
    ----------
    view : sublime.View
        A Sublime Text ``View`` object.
    file_extensions : list, optional
        The list of file extensions to check against.

    Returns
    -------
    bool
        Whether if file is of the right syntax.

    Note
    ----
    Borrowed from JSFormat.
    """
    file_name = get_file_path(view)
    ext = None

    if file_name:  # file exists, pull syntax type from extension
        ext = os.path.splitext(file_name)[1][1:]

    if ext is not None:
        return ext in file_extensions

    return False


def get_selections(view, return_whole_file=True, extract_words=False):
    """Get all selections.

    Parameters
    ----------
    view : sublime.View
        A Sublime Text ``View`` object.
    return_whole_file : bool, optional
        If all selections are empty, return the whole view content.
    extract_words : bool, optional
        If no selection is found at region's coordinates, extract words from regions.

    Returns
    -------
    list
        A list of regions.
    """
    selections = []

    if view:
        for region in view.sel():
            if extract_words and region.empty():
                word = view.word(region)

                if word:
                    selections.append(word)
                    continue

            if not region.empty():
                selections.append(region)

        if len(selections) == 0 and return_whole_file:
            selections.append(sublime.Region(0, view.size()))

    return selections


def replace_all_selections(view, edit, replacement_data):
    """Replace all selections.

    Parameters
    ----------
    view : sublime.View
        A Sublime Text ``View`` object.
    edit : sublime.Edit
        A Sublime Text ``Edit`` object.
    replacement_data : list
        A list of tuples with two elements. The first element is a ``sublime.Region`` and the
        second element is the text that will be placed into the region.
    """
    offset = 0

    for old_region, new_data in sorted(replacement_data, key=lambda t: t[0].begin()):
        if offset:
            new_region = sublime.Region(
                old_region.begin() + offset, old_region.end() + offset
            )
        else:
            new_region = old_region

        offset += len(new_data) - old_region.size()

        view.replace(edit, new_region, new_data)


def get_executable_from_settings(view, exec_list):
    """Get executable.

    Parameters
    ----------
    view : sublime.View
        A Sublime Text ``View`` object.
    exec_list : str, list
        The list of executable names and/or paths to check.

    Returns
    -------
    str
        The path or name to an existent program.
    None
        No program found.
    """
    exec_list = substitute_variables(get_view_context(view), exec_list)

    if isinstance(exec_list, str):
        exec_list = [exec_list]

    for exec in exec_list:
        if exec and (cmd_utils.can_exec(exec) or cmd_utils.which(exec)):
            return exec

    return None


def substitute_variables(variables, value):
    """Substitute variables.

    Utilizes Sublime Text's `expand_variables` API, which uses the `${varname}` syntax and
    supports placeholders (`${varname:placeholder}`).

    Parameters
    ----------
    variables : dict
        A dictionary containing variables as keys mapped to values to replace those variables.
    value : str, list, dict
        The str/list/dict containing the data where to perform substitutions.

    Returns
    -------
    list
    dict
    str
        The modified data.

    Note
    ----
    Borrowed from SublimeLinter.
    """
    if isinstance(value, str):
        # Workaround https://github.com/SublimeTextIssues/Core/issues/1878
        # (E.g. UNC paths on Windows start with double backslashes.)
        value = value.replace(r"\\", r"\\\\")

        if os.pardir + os.sep in value:
            value = os.path.normpath(value)

        value = os.path.expandvars(os.path.expanduser(value))

        return sublime.expand_variables(value, variables)
    elif isinstance(value, Mapping):
        return {key: substitute_variables(variables, val) for key, val in value.items()}
    elif isinstance(value, Sequence):
        return [substitute_variables(variables, item) for item in value]
    else:
        return value


def guess_project_root_of_view(view):
    """Guess project root folder from view.

    Parameters
    ----------
    view : sublime.View
        A Sublime Text ``View`` object.

    Returns
    -------
    None
        No project root folder could be ascertained.
    str
        The project root folder.

    Note
    ----
    Borrowed from SublimeLinter. I <3 these guys!
    """
    window = view.window()
    if not window:
        return None

    folders = window.folders()
    if not folders:
        return None

    filename = get_file_path(view)

    if not filename:
        return folders[0]

    for folder in folders:
        # Take the first one; should we take the deepest one? The shortest?
        if os.path.commonprefix([folder, filename]) == folder:
            return folder

    return None


def get_file_path(view):
    """Get file from view.

    Parameters
    ----------
    view : sublime.View
        A Sublime Text ``View`` object.

    Returns
    -------
    str
        The view's file path.
    """
    file_path = view.file_name()
    return str(file_path) if view and file_path else ""


def get_filename(view):
    """Get view's file name.

    Parameters
    ----------
    view : sublime.View
        A Sublime Text ``View`` object.

    Returns
    -------
    str
        File name.

    Note
    ----
    Borrowed from SublimeLinter.
    """
    file_path = get_file_path(view)
    return (
        os.path.basename(file_path)
        if file_path
        else "<untitled {}>".format(view.buffer_id())
    )


def _extract_window_variables(window):
    """Extract window variables.

    We explicitly want to compute all variables around the current file on our own.

    Parameters
    ----------
    window : sublime.Window
        A Sublime Text ``Window`` object.

    Returns
    -------
    dict
        Window variables.
    """
    variables = window.extract_variables()

    for key in ("file", "file_path", "file_name", "file_base_name", "file_extension"):
        variables.pop(key, None)

    return variables


def get_view_context(view, additional_context=None):
    """Get view context.

    Note that we ship a enhanced version for ``folder`` if you have multiple
    folders open in a window. See ``guess_project_root_of_view``.

    Parameters
    ----------
    view : sublime.View
        A Sublime Text ``View`` object.
    additional_context : None, optional
        Additional context.

    Returns
    -------
    collections.ChainMap
        Extended window variables with environment variables and more "persistent"
        files/folders names/paths.
    """
    view = view or sublime.active_window().active_view()
    window = view.window() if view else sublime.active_window()
    context = ChainMap(
        {}, _extract_window_variables(window) if window else {}, os.environ
    )

    project_folder = guess_project_root_of_view(view)

    if project_folder:
        context["folder"] = project_folder

    # ``window.extract_variables`` actually resembles data from the
    # ``active_view``, so we need to pass in all the relevant data around
    # the filename manually in case the user switches to a different
    # view, before we're done here.
    filename = get_file_path(view)

    if filename:
        basename = os.path.basename(filename)
        file_base_name, file_extension = os.path.splitext(basename)

        context["file"] = filename
        context["file_path"] = os.path.dirname(filename)
        context["file_name"] = basename
        context["file_base_name"] = file_base_name
        context["file_extension"] = file_extension

    context["canonical_filename"] = get_filename(view)

    if additional_context:
        context.update(additional_context)

    return context


def reload_plugins(prefix):
    """Reload Sublime 'plugins' using official API.

    Parameters
    ----------
    prefix : str
        Python module prefix.
    """
    toplevel = []
    for name, module in sys.modules.items():
        if name.startswith(prefix):
            depth = len(name.split("."))
            if depth == 2:
                toplevel.append(name)

    for name in sorted(toplevel):
        sublime_plugin.reload_plugin(name)


def generate_keybindings_help_data(
    help_data_commands, help_data_markup, spacer="&nbsp;", logger=None
):
    """Generate keybindings help data.

    Parameters
    ----------
    help_data_commands : dict
        Description
    help_data_markup : str
        Description
    spacer : str, optional
        Description
    logger : None, optional
        Description
    """
    res_path = substitute_variables(
        get_view_context(None), "Packages/User/Default ($platform).sublime-keymap"
    )

    try:
        res = sublime.decode_value(sublime.load_resource(res_path))
    except Exception as err:
        if logger:
            logger.error(err)

        return None

    desired_commands_set = set([d["command"] for d in help_data_commands.values()])
    filtered_keybindings = [kb for kb in res if (kb["command"] in desired_commands_set)]
    joined_keys = []
    help_data_keys = {}

    for help_text, cmd_data in help_data_commands.items():
        for kb in filtered_keybindings:
            keys_list = kb.get("keys", None)
            if all(
                (
                    cmd_data.get("args", None) == kb.get("args", None),
                    cmd_data["command"] == kb.get("command", None),
                    keys_list,
                )
            ):
                keys_str = ", ".join(keys_list)
                joined_keys.append(keys_str)

                if help_text in help_data_keys:
                    help_data_keys[help_text].append(keys_str)
                else:
                    help_data_keys[help_text] = [keys_str]

    help_markup = ""
    justification = len(max(joined_keys, key=len)) + 2

    for help_text, keys in help_data_keys.items():
        keys.sort()
        last_key = keys[-1]
        rest_of_keys = keys[:-1]

        for key in rest_of_keys:
            help_markup += help_data_markup.format(key=key, description="") + "\n"

        help_markup += (
            help_data_markup.format(
                key=last_key.ljust(justification, "|").replace("|", spacer),
                description=help_text,
            )
            + "\n"
        )

    return help_markup


if __name__ == "__main__":
    pass
