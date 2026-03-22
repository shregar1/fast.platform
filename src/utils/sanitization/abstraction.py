"""Base types for :mod:`utils.sanitization`."""

from __future__ import annotations

from utils.abstraction import IUtility


class ISanitization(IUtility):
    """Marker for helpers under :mod:`utils.sanitization` (functions or future classes)."""

    __slots__ = ()


__all__ = ["ISanitization"]
