# -*- coding: utf-8 -*-
"""Typing.

This folder is called **_vendor** just to force the ``stubgen`` command (provided by the **mypy**
package) to ignore it when generating stubs. And I'm forced to ignore it because ``stubgen`` mangles
the stubs of classes that have keyword arguments in their signatures.

.. code-block:: python

    class Whatever(TypedDict, total=False):
        attr_1: str
        attr_2: bool

...becomes the following stub:

.. code-block:: python

    class Whatever(TypedDict):
        attr_1: str
        attr_2: bool

Which renders the stub completely useless.
"""
