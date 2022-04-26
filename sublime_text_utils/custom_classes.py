# -*- coding: utf-8 -*-
"""Custom classes.
"""
import sublime


class CustomListInputItem(sublime.ListInputItem):
    """A ``sublime.ListInputItem`` that implements "rich comparison" methods.

    Attributes
    ----------
    prop_for_sort : str
        Property to store data for sorting used in case that the data stored in the default
        properties of a ``sublime.ListInputItem`` object aren't usefull/needed/wanted for sorting.
    """

    def __init__(
        self, *args, prop_for_sort_val=None, sort_prop="text", transform=str, **kwargs
    ):
        """Initialization.

        Parameters
        ----------
        *args
            Arguments to pass to ``sublime.ListInputItem``.
        prop_for_sort_val : any, None, optional
            The value for the ``prop_for_sort`` property. It would only make sense to store this
            value if the ``sort_prop`` parameter is set to ``prop_for_sort``.
        sort_prop : str, optional
            The name of the property that should be used when sorting a list of these items.
        transform : function, optional
            Function to call to transform the data that is going to be sorted.
        **kwargs
            Keyword arguments to pass to ``sublime.ListInputItem``.
        """
        sublime.ListInputItem.__init__(self, *args, **kwargs)
        self._sort_prop = sort_prop
        self._transform = transform
        self.prop_for_sort = prop_for_sort_val

    def __lt__(self, other):
        """Less than comparison.

        Parameters
        ----------
        other : CustomListInputItem
            The other instance to compare to.

        Returns
        -------
        bool
            Result of the comparison.
        """
        return self._transform(getattr(self, self._sort_prop)) < self._transform(
            getattr(other, self._sort_prop)
        )

    def __gt__(self, other):
        """Greater than comparison.

        Parameters
        ----------
        other : CustomListInputItem
            The other instance to compare to.

        Returns
        -------
        bool
            Result of the comparison.
        """
        return self._transform(getattr(self, self._sort_prop)) > self._transform(
            getattr(other, self._sort_prop)
        )

    def __le__(self, other):
        """Less than or equal comparison.

        Parameters
        ----------
        other : CustomListInputItem
            The other instance to compare to.

        Returns
        -------
        bool
            Result of the comparison.
        """
        return self._transform(getattr(self, self._sort_prop)) <= self._transform(
            getattr(other, self._sort_prop)
        )

    def __ge__(self, other):
        """Greater than or equal comparison.

        Parameters
        ----------
        other : CustomListInputItem
            The other instance to compare to.

        Returns
        -------
        bool
            Result of the comparison.
        """
        return self._transform(getattr(self, self._sort_prop)) >= self._transform(
            getattr(other, self._sort_prop)
        )

    def __eq__(self, other):
        """Equal comparison.

        Parameters
        ----------
        other : CustomListInputItem
            The other instance to compare to.

        Returns
        -------
        bool
            Result of the comparison.
        """
        return self._transform(getattr(self, self._sort_prop)) == self._transform(
            getattr(other, self._sort_prop)
        )

    def __ne__(self, other):
        """Non-equal comparison.

        Parameters
        ----------
        other : CustomListInputItem
            The other instance to compare to.

        Returns
        -------
        bool
            Result of the comparison.
        """
        return self._transform(getattr(self, self._sort_prop)) != self._transform(
            getattr(other, self._sort_prop)
        )


if __name__ == "__main__":
    pass
