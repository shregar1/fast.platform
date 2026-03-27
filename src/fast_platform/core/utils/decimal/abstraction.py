"""Base types for :mod:`utils.decimal`."""

from __future__ import annotations

from core.utils.abstraction import IUtility


class IDecimalUtility(IUtility):
    """Marker for decimal / money rounding helpers under :mod:`utils.decimal`."""

    __slots__ = ()


__all__ = ["IDecimalUtility"]
