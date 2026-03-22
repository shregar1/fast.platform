from __future__ import annotations

"""Section suite for ``PackageSection.OPERATIONS``."""

from abc import ABC

from tests.abstraction import ITest


class IOperationsSuite(ITest, ABC):
    """Marker for test classes under taxonomy section ``operations``."""

    __slots__ = ()


__all__ = ["IOperationsSuite"]
