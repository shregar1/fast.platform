"""Base types for :mod:`utils.nutrition`."""

from __future__ import annotations

from ..abstraction import IUtility


class INutritionUtility(IUtility):
    """Marker for nutrition / macro math helpers under :mod:`utils.nutrition`."""

    __slots__ = ()


__all__ = ["INutritionUtility"]
