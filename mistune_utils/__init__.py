# -*- coding: utf-8 -*-
"""Custom initialization and overrides for the mistune module.

..note:

    **Markdown parser additions/overrides**:

    - Added support for ``kbd`` tag. ``[[Ctrl]]`` will render as ``<kbd>Ctrl</kbd>``.
    - Added **table** and **table-bordered** classes to the ``<table>`` HTML tag.
    - Added **blockquote** class to the ``<blockquote>`` HTML tag.

Attributes
----------
md : Markdown
    A reusable instance of :py:class:`mistune.markdown.Markdown`.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..mistune.markdown import Markdown

from ..mistune import HTMLRenderer
from ..mistune import create_markdown

from .plugins.kbd import plugin_kbd


class MistuneCustomRenderer(HTMLRenderer):
    """Mistune custom renderer.
    """

    def block_quote(self, text: str) -> str:
        """Rendering <blockquote> with the given text.

        Override ``mistune.renderers.HTMLRenderer.block_quote`` to add the **blockquote** Bootstrap class.

        Parameters
        ----------
        text : str
            <blockquote> HTML tag content.

        Returns
        -------
        str
            HTML text.
        """
        return '<blockquote class="blockquote">%s\n</blockquote>\n' % text.rstrip("\n")

    def table(self, text: str) -> str:
        """Rendering table element.

        Override ``mistune.plugins.table.render_html_table`` to add the **table** and **table-bordered**
        Bootstrap classes.

        Parameters
        ----------
        text : str
            <table> HTML tag content.

        Returns
        -------
        str
            HTML text.
        """
        return '<table class="table table-bordered">\n%s\n</table>\n' % text


_mistune_renderer: MistuneCustomRenderer = MistuneCustomRenderer()


md: Markdown = create_markdown(
    escape=True,
    renderer=_mistune_renderer,
    plugins=["url", "strikethrough", "table", plugin_kbd],
)


if __name__ == "__main__":
    pass
