from __future__ import annotations

from tests.data_platform.abstraction import IDataPlatformSuite

"""Test-suite markers for ``storage`` (mirrors ``src/storage/``)."""


from abc import ABC


class IStorageTests(IDataPlatformSuite, ABC):
    """Marker base for test classes covering :mod:`storage`."""

    __slots__ = ()


__all__ = ["IStorageTests"]
