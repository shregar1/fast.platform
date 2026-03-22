from __future__ import annotations

"""Section suite for ``PackageSection.INTEGRATIONS``."""

from abc import ABC

from tests.abstraction import ITest


class IIntegrationsSuite(ITest, ABC):
    """Marker for test classes under taxonomy section ``integrations``."""

    __slots__ = ()


__all__ = ["IIntegrationsSuite"]
