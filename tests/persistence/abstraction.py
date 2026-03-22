from __future__ import annotations

"""Section suite for ``PackageSection.PERSISTENCE``."""

from abc import ABC

from tests.abstraction import ITest


class IPersistenceSuite(ITest, ABC):
    """Marker for test classes under taxonomy section ``persistence``."""

    __slots__ = ()


__all__ = ["IPersistenceSuite"]
