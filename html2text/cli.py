# -*- coding: utf-8 -*-
"""Summary
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any

import argparse
import sys

from . import HTML2Text
from . import __version__
from . import config
from .utils import attr_to_cli


def main() -> None:
    """Main method.

    Raises
    ------
    err
        A UnicodeDecodeError if decoding errors are found when reading a file.
    """
    p: argparse.ArgumentParser = argparse.ArgumentParser()

    for opt_name, opt_def in config.VALID_OPTIONS.items():
        opt_type: type = opt_def["typ"]
        opt_default: Any = opt_def["default"]

        if opt_type is bool:
            p.add_argument(
                attr_to_cli(opt_name, opt_default),
                dest=opt_name,
                action="store_false" if opt_default else "store_true",
                default=opt_default,
                help=opt_def["doc"],
            )
        elif opt_type is str or opt_type is int:
            p.add_argument(
                attr_to_cli(opt_name, None),
                dest=opt_name,
                default=opt_default,
                type=opt_type,
                help=opt_def["doc"],
            )

    p.add_argument("--version", action="version", version=".".join(map(str, __version__)))
    p.add_argument(
        "--decode-errors",
        dest="decode_errors",
        default="strict",
        type=str,
        choices=["strict", "ignore", "replace"],
        help="How to handle decoding errors. Possible values: 'strict', 'ignore', 'replace'. It defaults to 'strict'.",
    )
    p.add_argument("filename", nargs="?", default=None)
    p.add_argument("encoding", nargs="?", default="utf-8")
    args: dict = dict(vars(p.parse_args()))

    # NOTE: The args "poping" is so I can re-use args as keyword arguments for the HTML2Text class.
    decode_errors: str = args.pop("decode_errors")
    filename: str | None = args.pop("filename")
    encoding: str = args.pop("encoding")
    data: bytes

    if filename and filename != "-":
        with open(filename, "rb") as fp:
            data = fp.read()
    else:
        data = sys.stdin.buffer.read()

    try:
        html: str = data.decode(encoding=encoding, errors=decode_errors)
    except UnicodeDecodeError as err:
        print("Warning: Use the --decode-errors=ignore flag.")
        raise err

    h = HTML2Text(**args)

    sys.stdout.write(h.handle(html))
