# -*- coding: utf-8 -*-
"""Command line menu creator.

Based on: `Menu module <https://pypi.python.org/pypi/Menu>`__.

.. note::

    **Modifications**:

    - Changed some default values to suit my needs.
    - Some aesthetic changes for better readability of the menu items on the screen.
    - This modified version doesn't clear the screen every time a menu is opened.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

from . import exceptions
from .ansi_colors import colorize


class Menu(object):
    """Easily create command-line menus.

    Attributes
    ----------
    is_message_enabled : bool
        Used to whether or not to display the menu message.
    is_open : bool
        Whether the menu is open or not.
    is_title_enabled : bool
        Used to whether or not to display the menu title.
    menu_items : list[tuple[str, Callable[..., None]]]
        The list of menu items to create the menu.
    message : str
        A message/description to use in the menu.
    prompt : str
        The character used as a prompt for the menu.
    refresh : Callable[..., None]
        A function to call before displaying the menu.
    title : str
        A title to use on the menu.
    """

    def __init__(
        self,
        menu_items: list[tuple[str, Callable[..., None]]] = [],
        title: str = "",
        message: str = "",
        prompt: str = "❯ ",
        refresh: Callable[..., None] = lambda: None,
    ) -> None:
        """Initialization.

        Parameters
        ----------
        menu_items : list[tuple[str, Callable[..., None]]], optional
            The list of menu items to create the menu.
        title : str, optional
            A title to use on the menu.
        message : str, optional
            A message/description to use in the menu.
        prompt : str, optional
            The character used as a prompt for the menu.
        refresh : Callable[..., None], optional
            A function to call before displaying the menu.
        """
        self.menu_items: list[tuple[str, Callable[..., None]]] = menu_items
        self.title: str = title
        self.is_title_enabled: bool = bool(title)
        self.message: str = message
        self.is_message_enabled: bool = bool(message)
        self.refresh: Callable[..., None] = refresh
        self.prompt: str = prompt
        self.is_open: bool = False

    def set_menu_items(self, menu_items: list[str]) -> None:
        """Set menu items.

        Parameters
        ----------
        menu_items : list[str]
            List of tuples used to create the menu itmes.

        Raises
        ------
        SystemExit
            Halt execution.
        TypeError
            If a menu item inside the menu list isn't a tuple.
        ValueError
            If the tuple lenght of the menu item inside the menu list is not equal to two (2).
        """
        original_menu_items: list[tuple[str, Callable[..., None]]] = self.menu_items
        self.menu_items = []

        try:
            for item in menu_items:
                if not isinstance(item, tuple):
                    print(item)
                    print(colorize("**TypeError:** item is not a tuple", "error"))
                    raise TypeError()

                if len(item) != 2:
                    print(item)
                    print(colorize("**ValueError:** item is not of length 2", "error"))
                    raise ValueError()

                self.add_menu_item(item[0], item[1])
        except (TypeError, ValueError):
            self.menu_items = original_menu_items
            raise SystemExit()

    def set_title(self, title: str) -> None:
        """Set title.

        Parameters
        ----------
        title : str
            The string used as the menu title.
        """
        self.title = title

    def set_title_enabled(self, is_enabled: bool) -> None:
        """Set title enabled.

        Parameters
        ----------
        is_enabled : bool
            Whether the menu title will be displayed or not.
        """
        self.is_title_enabled = is_enabled

    def set_message(self, message: str) -> None:
        """Set message.

        Parameters
        ----------
        message : str
            The string used as the menu message.
        """
        self.message = message

    def set_message_enabled(self, is_enabled: bool) -> None:
        """Set message enabled.

        Parameters
        ----------
        is_enabled : bool
            Whether the menu message will be displayed or not.
        """
        self.is_message_enabled = is_enabled

    def set_prompt(self, prompt: str) -> None:
        """Set prompt.

        Parameters
        ----------
        prompt : str
            The prompt character to be used by the menu.
        """
        self.prompt = prompt

    def set_refresh(self, refresh: Callable[..., None]) -> None:
        """Set refresh.

        Parameters
        ----------
        refresh : Callable[..., None]
            A function to call before displaying the menu.

        Raises
        ------
        TypeError
            Halt execution if the refresh method isn't a callable.
        """
        if not callable(refresh):
            print(refresh)
            print(colorize("**TypeError:** refresh is not callable", "error"))
            raise TypeError()

        self.refresh = refresh

    def add_menu_item(self, label: str, handler: Callable[..., None]) -> None:
        """Add menu item.

        Parameters
        ----------
        label : str
            The text used by a menu item.
        handler : Callable[..., None]
            The function to call when activating a menu item.

        Raises
        ------
        TypeError
            Halt execution if the handler method isn't a callable.
        """
        if not callable(handler):
            print(handler)
            print(colorize("**TypeError:** handler is not callable", "error"))
            raise TypeError()

        self.menu_items += [(label, handler)]

    def open(self) -> None:
        """Open menu.

        Raises
        ------
        exceptions.KeyboardInterruption
            Halt execution on Ctrl + C press.
        exceptions.OperationAborted
            Halt execution.
        """
        self.is_open = True

        try:
            while self.is_open:
                self.refresh()
                func: Callable[..., None] = self.input()

                if func == Menu.CLOSE:
                    func = self.close

                print()
                func()
        except KeyboardInterrupt:
            self.is_open = False
            raise exceptions.KeyboardInterruption()
        except SystemExit:
            self.is_open = False
            raise exceptions.OperationAborted("")

    def close(self) -> None:
        """Close menu."""
        self.is_open = False

    def show(self) -> None:
        """Display menu."""
        if self.is_title_enabled:
            print(colorize("**%s**" % self.title))
            print()

        if self.is_message_enabled:
            print(self.message)
            print()

        for (index, item) in enumerate(self.menu_items):
            print(colorize("**%s**" % str(index + 1) + ". "), end="")
            print(item[0])

        print()

    def input(self) -> Callable[..., None]:
        """Process input.

        Returns
        -------
        Callable[..., None]
            The method to call when a menu item is activated.
        """
        if len(self.menu_items) == 0:
            return Menu.CLOSE

        try:
            self.show()
            index: int = int(input(self.prompt)) - 1
            return self.menu_items[index][1]
        except (ValueError, IndexError):
            print(colorize("**Invalid item selected!**", "warning"))
            return self.input()

    def CLOSE(self) -> None:
        """Close menu."""
        pass


if __name__ == "__main__":
    pass
