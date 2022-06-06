# -*- coding: utf-8 -*-
"""Simple validator functions.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

import re

from ipaddress import ip_address

from . import exceptions
from . import file_utils


_hostname_regex: re.Pattern = re.compile(r"(?!-)[\w-]{1,63}(?<!-)$")


def is_valid_host(host: str) -> bool:
    """IDN compatible domain validation.

    Parameters
    ----------
    host : str
        The host name to check.

    Returns
    -------
    bool
        Whether the host name is valid or not.

    Note
    ----
    Based on: `Validate-a-hostname-string \
    <https://stackoverflow.com/questions/2532053/validate-a-hostname-string>`__
    """
    host = host.rstrip(".")

    return all(
        [len(host) > 1, len(host) < 253] + [bool(_hostname_regex.match(x)) for x in host.split(".")]
    )


def is_valid_ip(address: str) -> bool:
    """Validate IP address (IPv4 or IPv6).

    Parameters
    ----------
    address : str
        The IP address to validate.

    Returns
    -------
    bool
        If it is a valid IP address or not.
    """
    try:
        ip_address(address)
    except ValueError:
        return False

    return True


def is_valid_integer(integer: str | int) -> bool:
    """Validate integer.

    Parameters
    ----------
    integer : str | int
        The string to validate.

    Returns
    -------
    bool
        If the value is a valid integer or not.
    """
    return str(integer).isdigit()


def validate_output_path(x: str) -> str:
    """Validate output path.

    Checks that a given path is not a user's home folder nor "/".

    Parameters
    ----------
    x : str
        The entered option to validate.

    Returns
    -------
    str
        The validated option.

    Raises
    ------
    exceptions.ValidationError
        Halt execution if option is not valid.
    """
    if x == file_utils.expand_path("~") or x == "~":
        raise exceptions.ValidationError("Seriously, don't be daft! Choose another location!")
    elif x == "/":
        raise exceptions.ValidationError(
            "Are you freaking kidding me!? The root partition!? Use your brain!"
        )

    return x


def generate_numeral_options_validator(
    num: int, stringify: bool = True
) -> Callable[[str | int], str | int]:
    """Generate numeral options validator.

    Parameters
    ----------
    num : int
        The number of numbers that the list of numeral options should have. Starting
        from 1 and ending at and including num.
    stringify : bool, optional
        Whether the list of numbers should be converted and compared to numbers
        represented as strings.

    Returns
    -------
    Callable[[str | int], str | int]
        A function to validate a number.

    Raises
    ------
    exceptions.ValidationError
        Description
    """
    options_list = [str(n + 1) if stringify else n + 1 for n in list(range(num))]

    def validate_options(x: str | int) -> str | int:
        """Validate numeral options.

        Parameters
        ----------
        x : str | int
            The entered option to validate.

        Returns
        -------
        str | int
            The validated option.

        Raises
        ------
        exceptions.ValidationError
            Halt execution if option is not valid.
        """
        if not x or x not in options_list:
            raise exceptions.ValidationError("Possible options are: %s" % ", ".join(options_list))

        return x

    return validate_options


if __name__ == "__main__":
    pass
