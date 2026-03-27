"""Module abstraction.py."""

from __future__ import annotations

"""Section suite for ``PackageSection.CORE``."""

from abc import ABC

from tests.abstraction import ITest


class ICoreSuite(ITest, ABC):
    """Marker for test classes under taxonomy section ``core``."""

    __slots__ = ()


__all__ = ["ICoreSuite"]
