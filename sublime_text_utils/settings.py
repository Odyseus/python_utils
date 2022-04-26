# -*- coding: utf-8 -*-
"""Sublime Text plugin settings manager.
"""
from functools import wraps

import sublime
import sublime_plugin

from .. import misc_utils


class SettingsManager:
    """This class provides global access to and management of plugin settings.

    Attributes
    ----------
    events : Events
        Events manager.
    logger : SublimeLogger
        The logger.
    name_space : str
        This namespace is automatically generated from the snake cased ``settings_file`` parameter.
        It is used to define plugin settings inside a ``settings`` key in a project file.

    Note
    ----
    Borrowed from SublimeLinter.
    """

    def __init__(self, settings_file="Preferences", events=None, logger=None):
        """Initialization.

        Parameters
        ----------
        settings_file : str, optional
            This should be the name of a Sublime Text settings file. This is normally the name
            of a plugin folder and its ``.sublime-settings`` file that should be in pascal case.
        events : None, optional
            Events manager.
        logger : SublimeLogger
            The logger.
        """
        self.events = events
        self.logger = logger
        self.name_space = self._get_name_space(settings_file)
        self._is_native_settings = settings_file == "Preferences"
        self._pref_file = "%s.sublime-settings" % settings_file
        self._reload_key = misc_utils.get_date_time(type="function_name")
        self._previous_state = {}
        self._current_state = {}
        self.__project_settings = None
        self.__settings = None
        self._change_count = 0

    def load(self):
        """Load the plugin settings.
        """
        self.observe()
        self.on_update()

    def _get_name_space(self, name_space):
        """Get namespace key.

        Parameters
        ----------
        name_space : str
            Namespace.

        Returns
        -------
        str
            Namespace key.
        """
        name_space_key = name_space[0].lower()
        last_upper = False

        for c in name_space[1:]:
            if c.isupper() and not last_upper:
                name_space_key += "_"
                name_space_key += c.lower()
            else:
                name_space_key += c

            last_upper = c.isupper()

        return name_space_key

    @property
    def settings(self):
        """Get plugin settings.

        Returns
        -------
        dict
            A plugin settings object.
        """
        s = self.__settings

        if not s:
            s = self.__settings = sublime.load_settings(self._pref_file)

        return s

    @property
    def project_settings(self):
        """Get project settings.

        Returns
        -------
        dict
            A project settings object.
        """
        try:
            if self._is_native_settings:
                s = sublime.active_window().project_data().get("settings", {})
            else:
                s = (
                    sublime.active_window()
                    .project_data()
                    .get("settings", {})
                    .get(self.name_space, {})
                )
        except Exception:
            s = {}

        return s

    def has(self, name):
        """Return whether the given setting exists.

        Parameters
        ----------
        name : str
            The name of a setting.

        Returns
        -------
        bool
            If the named option exists.
        """
        return self.settings.has(name)

    def get(self, name, default=None):
        """Return a plugin setting, defaulting to default if not found.

        Parameters
        ----------
        name : str
            The name of a setting to get the value of.
        default : any, None, optional
            What value to return as a fallback.

        Returns
        -------
        any
            The setting value or the default value.
        """
        try:
            return self._current_state[name]
        except KeyError:
            global_value = self.settings.get(name, default)
            project_value = self.project_settings.get(name, global_value)
            self._current_state[name] = current_value = misc_utils.merge_dict(
                global_value,
                project_value,
                logger=self.logger,
                extend_lists=False,
                append_to_lists=False,
            )
            return current_value

    def set(self, name, value):
        """Set setting value.

        Parameters
        ----------
        name : str
            The name of the setting to change.
        value : any
            The new value for the setting.
        """
        try:
            self.__settings.set(name, value)
            sublime.save_settings(self._pref_file)
        except BaseException as err:
            self.logger.error(err)

    def has_changed(self, name):
        """Check if setting has changed.

        Parameters
        ----------
        name : str
            Name of the setting to check for changes.

        Returns
        -------
        bool
            If the setting has changed.
        """
        current_value = self.get(name)
        try:
            old_value = self._previous_state[name]
        except KeyError:
            return False
        else:
            return old_value != current_value

    def change_count(self):
        """Change count.

        Returns
        -------
        int
            Change count.
        """
        return self._change_count

    def observe(self):
        """Observe changes.
        """
        self.settings.clear_on_change(self._reload_key)
        self.settings.add_on_change(self._reload_key, self.on_update)

    def unobserve(self):
        """Stop observing for changes.
        """
        self.settings.clear_on_change(self._reload_key)

    def on_update(self):
        """Update state when the user settings change.
        """
        self._previous_state = self._current_state.copy()
        self._current_state.clear()
        self._change_count += 1

        if self.events:
            self.events.broadcast("settings_changed", {"settings_obj": self})


class SettingsToggleBoolean:
    """Toggle booleans.

    This is meant to be sub-classed with ``sublime_plugin.WindowCommand`` and be used on
    menu definitions.

    Attributes
    ----------
    ody_description : str
        Description to display as a label on a menu item.
    ody_false_label : str
        Text to display next to a menu item description when the controlled seting is false.
    ody_key : str
        The key of the setting to get the value of.
    ody_settings : settings.Settings
        The object from where to get the value of a setting.
    ody_true_label : str
        Text to display next to a menu item description when the controlled seting is true.
    """

    def __init__(self, *args, **kwargs):
        """Initialization.

        Parameters
        ----------
        *args
            Arguments.
        **kwargs
            Keyword arguments.
        """
        self.ody_key = kwargs.get("key", "")
        self.ody_settings = kwargs.get("settings", {})
        self.ody_description = kwargs.get("description", "")
        self.ody_true_label = kwargs.get("true_label", "Enabled")
        self.ody_false_label = kwargs.get("false_label", "Disabled")

    def run(self):
        """Action to perform when this Sublime Text command is executed.
        """
        try:
            new_val = not self.ody_settings.get(self.ody_key, False)
            self.ody_settings.set(self.ody_key, new_val)
            sublime.status_message("%s changed to %r" % (self.ody_key, new_val))
        except Exception as err:
            print(err)

    def is_checked(self):
        """Returns True if a checkbox should be shown next to the menu item.

        Returns
        -------
        bool
            Is checked.
        """
        return self.ody_settings.get(self.ody_key, False)

    def description(self):
        """Command description.

        Returns
        -------
        str
            The command description.
        """
        try:
            return self.ody_description.format(
                self.ody_true_label if self.is_checked() else self.ody_false_label
            )
        except IndexError:
            return self.ody_description


class SettingsToggleList:
    """Toggle list of values.

    This is meant to be sub-classed with a ``sublime_plugin.WindowCommand``, a
    ``sublime_plugin.TextCommand``, or ``sublime_plugin.ApplicationCommand`` and be used on
    menu definitions.

    Attributes
    ----------
    ody_description : str
        Description to display as a label on a menu item.
    ody_key : str
        The key of the setting to get the value of.
    ody_settings : settings.Settings
        The object from where to get the value of a setting.
    ody_values_list : list
        List of values for cycle through.
    """

    def __init__(self, **kwargs):
        """Initialization.

        Parameters
        ----------
        **kwargs
            Keyword arguments.
        """
        self.ody_key = kwargs.get("key", "")
        self.ody_settings = kwargs.get("settings", {})
        self.ody_description = kwargs.get("description", "")
        self.ody_values_list = kwargs.get("values_list", [])

    def run(self):
        """Action to perform when this Sublime Text command is executed.
        """
        try:
            old_val = self.ody_settings.get(self.ody_key, "")
            new_val = self.ody_get_new_value(old_val)
            self.ody_settings.set(self.ody_key, new_val)
            sublime.status_message("%s changed to %r" % (self.ody_key, new_val))
        except Exception as err:
            print(err)

    def ody_get_new_value(self, old_val):
        """Get new value from the list of possible values.

        Parameters
        ----------
        old_val : str
            The old value.

        Returns
        -------
        any
            The new value.
        """
        try:
            # Get index of value that's after current value.
            val_idx = self.ody_values_list.index(old_val) + 1
        except ValueError:
            # Fallback to index 0.
            val_idx = 0

        try:
            return self.ody_values_list[val_idx]
        except IndexError:
            return self.ody_values_list[0]

    def description(self):
        """Command description.

        Returns
        -------
        str
            The command description.
        """
        try:
            return self.ody_description.format(self.ody_settings.get(self.ody_key, ""))
        except IndexError:
            return self.ody_description


def distinct_until_buffer_changed(method):
    """Distinct until buffer changed.

    Sublime has problems to hold the distinction between buffers and views.
    It usually emits multiple identical events if you have multiple views
    into the same buffer.

    Parameters
    ----------
    method : method
        Method to wrap.

    Returns
    -------
    method
        Wrapped method.
    """
    last_call = None

    @wraps(method)
    def wrapper(self, view):
        """Wrapper.

        Parameters
        ----------
        view : object
            An instance of ``sublime.View``.

        Returns
        -------
        None
            Halt execution.
        """
        nonlocal last_call

        this_call = (view.buffer_id(), view.change_count())
        if this_call == last_call:
            return

        last_call = this_call
        method(self, view)

    return wrapper


class ProjectSettingsController(sublime_plugin.EventListener):
    """Monitor changes to a project settings file to allow re-loading of an instance of SettingsManager.
    """

    def _on_post_save_async(self, view, settings):
        """Called after a view has been saved.

        Parameters
        ----------
        view : sublime.View
            A Sublime Text ``View`` object.
        settings : SettingsManager
            An instance of ``SettingsManager``.
        """
        window = view.window()
        filename = view.file_name()
        if window and filename and window.project_file_name() == filename:
            for window in sublime.windows():
                if window.project_file_name() == filename:
                    settings.load()


if __name__ == "__main__":
    pass
