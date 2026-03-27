"""Base types for :mod:`utils.sanitization`."""

from __future__ import annotations

from ..abstraction import IUtility


class ISanitization(IUtility):
    """Marker for sanitization utility classes under :mod:`utils.sanitization`."""

    __slots__ = ()


__all__ = ["ISanitization"]
