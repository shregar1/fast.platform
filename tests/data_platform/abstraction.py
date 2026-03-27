"""Module abstraction.py."""

from __future__ import annotations

"""Section suite for ``PackageSection.DATA_PLATFORM``."""

from abc import ABC

from tests.abstraction import ITest


class IDataPlatformSuite(ITest, ABC):
    """Marker for test classes under taxonomy section ``data_platform``."""

    __slots__ = ()


__all__ = ["IDataPlatformSuite"]
