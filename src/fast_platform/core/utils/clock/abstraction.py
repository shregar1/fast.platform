"""Base types for :mod:`utils.clock`."""

from __future__ import annotations

from ..abstraction import IUtility


class IClockUtility(IUtility):
    """Marker for injectable clocks and clock registry under :mod:`utils.clock`."""

    __slots__ = ()


__all__ = ["IClockUtility"]
