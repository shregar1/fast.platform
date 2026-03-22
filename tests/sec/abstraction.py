from __future__ import annotations

"""Section suite for ``PackageSection.SECURITY``."""

from abc import ABC

from tests.abstraction import ITest


class ISecuritySuite(ITest, ABC):
    """Marker for test classes under taxonomy section ``sec``."""

    __slots__ = ()


__all__ = ["ISecuritySuite"]
