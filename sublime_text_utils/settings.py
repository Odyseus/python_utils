# -*- coding: utf-8 -*-
"""Sublime Text plugin settings manager.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable
    from python_utils import logging_system
    from python_utils.sublime_text_utils.events import Events
    from typing import Any

from functools import wraps

import sublime
import sublime_plugin

from .. import misc_utils


class SettingsManager:
    """This class provides global access to and management of plugin settings.

    Attributes
    ----------
    events : Events | None
        Events manager.
    logger : logging_system.Logger | None
        The logger.
    name_space : str
        This namespace is automatically generated from the snake cased ``settings_file`` parameter.
        It is used to define plugin settings inside a ``settings`` key in a project file.

    Note
    ----
    Borrowed from SublimeLinter.
    """

    def __init__(
        self,
        settings_file: str = "Preferences",
        events: Events | None = None,
        logger: logging_system.Logger | None = None,
    ) -> None:
        """Initialization.

        Parameters
        ----------
        settings_file : str, optional
            This should be the name of a Sublime Text settings file. This is normally the name
            of a plugin folder and its ``.sublime-settings`` file that should be in pascal case.
        events : Events | None, optional
            Events manager.
        logger : logging_system.Logger | None, optional
            The logger.
        """
        self.events: Events | None = events
        self.logger: logging_system.Logger | None = logger
        self.name_space: str = self._get_name_space(settings_file)
        self._is_native_settings: bool = settings_file == "Preferences"
        self._pref_file: str = "%s.sublime-settings" % settings_file
        self._reload_key: str = misc_utils.get_date_time(type="function_name")
        self._previous_state: dict = {}
        self._current_state: dict = {}
        self.__project_settings: dict = {}
        self.__settings: sublime.Settings = None
        self._change_count: int = 0

    def load(self) -> None:
        """Load the plugin settings."""
        self.__project_settings.clear()
        self.observe()
        self.on_update()

    def _get_name_space(self, settings_file: str) -> str:
        """Get namespace key.

        Parameters
        ----------
        settings_file : str
            The name of a sublime-settings file without its extension.

        Returns
        -------
        str
            Namespace key.
        """
        name_space_key: str = settings_file[0].lower()
        last_upper: bool = False

        for c in settings_file[1:]:
            if c.isupper() and not last_upper:
                name_space_key += "_"
                name_space_key += c.lower()
            else:
                name_space_key += c

            last_upper = c.isupper()

        return name_space_key

    @property
    def settings(self) -> sublime.Settings:
        """Get plugin settings.

        Returns
        -------
        sublime.Settings
            A plugin settings object.
        """
        s: sublime.Settings = self.__settings

        if s is None:
            s = self.__settings = sublime.load_settings(self._pref_file)

        return s

    @property
    def project_settings(self) -> dict:
        """Get project settings.

        Returns
        -------
        dict
            A project settings object.
        """
        s: dict = self.__project_settings

        if not s:
            try:
                if self._is_native_settings:
                    s = self.__project_settings = (
                        sublime.active_window().project_data().get("settings", {})
                    )
                else:
                    s = self.__project_settings = (
                        sublime.active_window()
                        .project_data()
                        .get("settings", {})
                        .get(self.name_space, {})
                    )
            except Exception:
                s = {}

        return s

    def has(self, name: str) -> bool:
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

    def get(self, name: str, default: Any = None) -> Any:
        """Return a plugin setting, defaulting to default if not found.

        Parameters
        ----------
        name : str
            The name of a setting to get the value of.
        default : Any, optional
            What value to return as a fallback.

        Returns
        -------
        Any
            The setting value or the default value.
        """
        try:
            return self._current_state[name]
        except KeyError:
            global_value: Any = self.settings.get(name, default)
            project_value: Any = self.project_settings.get(name, global_value)
            self._current_state[name] = project_value
            return project_value

    def set(self, name: str, value: Any) -> None:
        """Set setting value.

        Parameters
        ----------
        name : str
            The name of the setting to change.
        value : Any
            The new value for the setting.
        """
        try:
            self.__settings.set(name, value)
            sublime.save_settings(self._pref_file)
        except BaseException as err:
            if self.logger is not None:
                self.logger.error(err)

    def has_changed(self, name: str) -> bool:
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
        current_value: Any = self.get(name)
        try:
            old_value: Any = self._previous_state[name]
        except KeyError:
            return False
        else:
            return old_value != current_value

    def change_count(self) -> int:
        """Change count.

        Returns
        -------
        int
            Change count.
        """
        return self._change_count

    def observe(self) -> None:
        """Observe changes."""
        self.settings.clear_on_change(self._reload_key)
        self.settings.add_on_change(self._reload_key, self.on_update)

    def unobserve(self) -> None:
        """Stop observing for changes."""
        self.settings.clear_on_change(self._reload_key)

    def on_update(self) -> None:
        """Update state when the user settings change."""
        self._previous_state = self._current_state.copy()
        self._current_state.clear()
        self._change_count += 1

        if self.events is not None:
            self.events.broadcast("settings_changed", {"settings_obj": self})


class SettingsToggleBoolean:
    """Toggle booleans.

    This is meant to be sub-classed with a ``sublime_plugin.WindowCommand``, a
    ``sublime_plugin.TextCommand``, or ``sublime_plugin.ApplicationCommand`` and be used on
    menu definitions.

    Attributes
    ----------
    ody_description : str
        Description to display as a label on a menu item.
    ody_false_label : str
        Text to display next to a menu item description when the controlled seting is false.
    ody_key : str
        The key of the setting to get the value of.
    ody_settings : SettingsManager
        The object from where to get the value of a setting.
    ody_true_label : str
        Text to display next to a menu item description when the controlled seting is true.
    """

    def __init__(self, *args, **kwargs) -> None:
        """See :py:meth:`object.__init__`.

        Parameters
        ----------
        *args
            Arguments.
        **kwargs
            Keyword arguments.
        """
        self.ody_key: str = kwargs.get("key", "")
        self.ody_settings: SettingsManager = kwargs.get("settings", {})
        self.ody_description: str = kwargs.get("description", "")
        self.ody_true_label: str = kwargs.get("true_label", "Enabled")
        self.ody_false_label: str = kwargs.get("false_label", "Disabled")

    def run(self, *args, **kwargs) -> None:
        """Action to perform when this Sublime Text command is executed.

        Parameters
        ----------
        *args
            Arguments.
        **kwargs
            Keyword arguments.
        """
        try:
            new_val: bool = not self.ody_settings.get(self.ody_key, False)
            self.ody_settings.set(self.ody_key, new_val)
            sublime.status_message("%s changed to %r" % (self.ody_key, new_val))
        except Exception as err:
            print(err)

    def is_checked(self) -> bool:
        """Returns True if a checkbox should be shown next to the menu item.

        Returns
        -------
        bool
            Is checked.
        """
        return self.ody_settings.get(self.ody_key, False)

    def description(self) -> str:
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
    ody_settings : SettingsManager
        The object from where to get the value of a setting.
    ody_values_list : list[str]
        List of values for cycle through.
    """

    def __init__(self, **kwargs) -> None:
        """Initialization.

        Parameters
        ----------
        **kwargs
            Keyword arguments.
        """
        self.ody_key: str = kwargs.get("key", "")
        self.ody_settings: SettingsManager = kwargs.get("settings", {})
        self.ody_description: str = kwargs.get("description", "")
        self.ody_values_list: list[str] = kwargs.get("values_list", [])

    def run(self, *args, **kwargs) -> None:
        """Action to perform when this Sublime Text command is executed.

        Parameters
        ----------
        *args
            Arguments.
        **kwargs
            Keyword arguments.
        """
        try:
            old_val: str = self.ody_settings.get(self.ody_key, "")
            new_val: str = self.ody_get_new_value(old_val)
            self.ody_settings.set(self.ody_key, new_val)
            sublime.status_message("%s changed to %r" % (self.ody_key, new_val))
        except Exception as err:
            print(err)

    def ody_get_new_value(self, old_val: str) -> str:
        """Get new value from the list of possible values.

        Parameters
        ----------
        old_val : str
            The old value.

        Returns
        -------
        str
            The new value.
        """
        val_idx: int = 0

        try:
            # Get index of value that's after current value.
            val_idx = self.ody_values_list.index(old_val) + 1
        except ValueError:
            pass

        try:
            return self.ody_values_list[val_idx]
        except IndexError:
            return self.ody_values_list[0]

    def description(self) -> str:
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


def distinct_until_buffer_changed(method: Callable[..., None]) -> Callable[..., None]:
    """Distinct until buffer changed.

    Sublime has problems to hold the distinction between buffers and views.
    It usually emits multiple identical events if you have multiple views
    into the same buffer.

    Parameters
    ----------
    method : Callable[..., None]
        Method to wrap.

    Returns
    -------
    Callable[..., None]
        Wrapped method.
    """
    last_call: tuple[int, int] = (0, 0)

    @wraps(method)
    def wrapper(self: object, view: sublime.View) -> None:
        """Wrapper.

        Parameters
        ----------
        view : sublime.View
            A Sublime Text ``View`` object.

        Returns
        -------
        None
            Halt execution.
        """
        nonlocal last_call

        this_call: tuple[int, int] = (view.buffer_id(), view.change_count())
        if this_call == last_call:
            return

        last_call = this_call
        method(self, view)

    return wrapper


class ProjectSettingsController(sublime_plugin.EventListener):
    """Monitor changes to a project settings file to allow re-loading of an instance of SettingsManager."""

    def _on_post_save_async(self, view: sublime.View, settings: SettingsManager) -> None:
        """Called after a view has been saved.

        Parameters
        ----------
        view : sublime.View
            A Sublime Text ``View`` object.
        settings : SettingsManager
            An instance of ``SettingsManager``.
        """
        window: sublime.Window = view.window()
        filename: str | None = view.file_name()
        if window and filename and window.project_file_name() == filename:
            for window in sublime.windows():
                if window.project_file_name() == filename:
                    settings.load()


if __name__ == "__main__":
    pass
