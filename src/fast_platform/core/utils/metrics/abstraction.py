"""Base types for :mod:`utils.metrics`."""

from __future__ import annotations

from ..abstraction import IUtility


class IMetricsUtility(IUtility):
    """Marker for in-process counters, histograms, and registry under :mod:`utils.metrics`."""

    __slots__ = ()


__all__ = ["IMetricsUtility"]
