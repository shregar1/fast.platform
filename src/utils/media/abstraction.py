"""Base types for :mod:`utils.media`."""

from __future__ import annotations

from utils.abstraction import IUtility


class IMedia(IUtility):
    """Marker base for utility classes under :mod:`utils.media`."""

    __slots__ = ()


__all__ = ["IMedia"]
