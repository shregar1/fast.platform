"""Base types for :mod:`utils.currency`."""

from __future__ import annotations

from ..abstraction import IUtility


class ICurrencyUtility(IUtility):
    """Marker for currency major/minor helpers under :mod:`utils.currency`."""

    __slots__ = ()


__all__ = ["ICurrencyUtility"]
