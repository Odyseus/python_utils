# -*- coding: utf-8 -*-
"""Common utilities to get files/directories hashes.

Attributes
----------
HASH_FUNCS : dict
    Hash functions.
"""
from __future__ import annotations

import hashlib
import os

HASH_FUNCS: dict = {
    "md5": hashlib.md5,
    "sha1": hashlib.sha1,
    "sha256": hashlib.sha256,
    "sha512": hashlib.sha512,
}

__blocksize = 128 * 1024


def dir_hash(dirname: str, hashfunc: str = "sha256", followlinks: bool = False) -> str:
    """Get directory hash.

    Parameters
    ----------
    dirname : str
        Path to a directory.
    hashfunc : str, optional
        Hash function to use.
    followlinks : bool, optional
        See :any:`os.walk`.

    Returns
    -------
    str
        A directory hash.

    Raises
    ------
    NotImplementedError
        If an invalid hash function is passed.
    """
    hash_func: type[hashlib._Hash] | None = HASH_FUNCS.get(hashfunc, None)

    if hash_func is None:
        raise NotImplementedError("{} not implemented.".format(hashfunc))

    hashvalues: list[str] = []

    for root, dirs, files in os.walk(dirname, topdown=True, followlinks=followlinks):
        hashvalues.extend(
            [file_hash(os.path.join(root, f), hasher=hash_func) for f in sorted(files)]
        )

    return _reduce_hash(hashvalues, hash_func)


def file_hash(filepath: str, hashfunc: str = "sha256", hasher: type[hashlib._Hash] | None = None) -> str:
    """Get file hash.

    Parameters
    ----------
    filepath : str
        Path to a file.
    hashfunc : str, optional
        The name of a hash function.
    hasher : hashlib._Hash | None, optional
        A hash function.

    Returns
    -------
    str
        A file hash.

    Raises
    ------
    NotImplementedError
        If an invalid hash function is passed.
    """
    h: hashlib._Hash = (
        hasher() if hasher is not None else HASH_FUNCS.get(hashfunc)()
    )

    if not h:
        raise NotImplementedError("{} not implemented.".format(hashfunc))

    with open(filepath, "rb", buffering=0) as f:
        for b in iter(lambda: f.read(__blocksize), b""):
            h.update(b)

    return h.hexdigest()


def _reduce_hash(hashlist: list[str], hashfunc: type[hashlib._Hash]) -> str:
    """Reduce hash.

    Parameters
    ----------
    hashlist : list[str]
        A list of hashes.
    hashfunc : hashlib._Hash
        The hash function to use.

    Returns
    -------
    str
        A hash.
    """
    h: hashlib._Hash = hashfunc()

    for hashvalue in sorted(hashlist):
        h.update(hashvalue.encode("utf-8"))

    return h.hexdigest()


if __name__ == "__main__":
    pass
