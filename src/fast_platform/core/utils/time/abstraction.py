"""Base types for :mod:`utils.time`."""

from __future__ import annotations

from ..abstraction import IUtility


class ITimeUtility(IUtility):
    """Marker for timezone / ISO-8601 helpers under :mod:`utils.time`."""

    __slots__ = ()


__all__ = ["ITimeUtility"]
