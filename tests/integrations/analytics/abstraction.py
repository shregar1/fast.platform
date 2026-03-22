from __future__ import annotations

from tests.integrations.abstraction import IIntegrationsSuite

"""Test-suite markers for ``analytics`` (mirrors ``src/analytics/``)."""


from abc import ABC


class IAnalyticsTests(IIntegrationsSuite, ABC):
    """Marker base for test classes covering :mod:`analytics`."""

    __slots__ = ()


__all__ = ["IAnalyticsTests"]
