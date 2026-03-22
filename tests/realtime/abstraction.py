from __future__ import annotations

"""Section suite for ``PackageSection.REALTIME``."""

from abc import ABC

from tests.abstraction import ITest


class IRealtimeSuite(ITest, ABC):
    """Marker for test classes under taxonomy section ``realtime``."""

    __slots__ = ()


__all__ = ["IRealtimeSuite"]
