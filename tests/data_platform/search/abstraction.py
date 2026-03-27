"""Module abstraction.py."""

from __future__ import annotations

from tests.data_platform.abstraction import IDataPlatformSuite

"""Test-suite markers for ``search`` (mirrors ``src/search/``)."""


from abc import ABC


class ISearchTests(IDataPlatformSuite, ABC):
    """Marker base for test classes covering :mod:`search`."""

    __slots__ = ()


__all__ = ["ISearchTests"]
