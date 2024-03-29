# -*- coding: utf-8 -*-
"""Module to download files. It displays a progress bar of the download progress.
"""
# NOTE: Web developers can go f*ck themselves!!!
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

from urllib.request import urlretrieve

from .tqdm import tqdm


class TqdmUpTo(tqdm):
    """Provides ``update_to(n)`` which uses ``tqdm.update(delta_n)``.

    Inspired by `twine#242 <https://github.com/pypa/twine/pull/242>`__,
    `here <https://github.com/pypa/twine/commit/42e55e06>`__.

    Attributes
    ----------
    total : int
        The number of expected iterations.
    """

    def update_to(self, b: int = 1, bsize: int = 1, tsize: int | None = None) -> None:
        """Update to.

        Parameters
        ----------
        b : int, optional
            Number of blocks transferred so far (default: 1).
        bsize : int, optional
            Size of each block (in tqdm units) (default: 1).
        tsize : int | None, optional
            Total size (in tqdm units). If (default: None) remains unchanged.
        """
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)  # will also set self.n = b * bsize


def download(url: str, filename: str) -> None:
    """Download file.

    Parameters
    ----------
    url : str
        The URL to the file to download.
    filename : str
        Downloaded file destination.
    """
    with TqdmUpTo(unit="B", unit_scale=True, unit_divisor=1024, miniters=1) as t:
        urlretrieve(url, filename=filename, reporthook=t.update_to, data=None)
        t.total = t.n


if __name__ == "__main__":
    pass
