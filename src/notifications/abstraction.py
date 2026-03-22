"""notifications package abstractions."""

from __future__ import annotations

from abc import ABC


class INotification(ABC):
    """Marker base for concrete types in the ``notifications`` package."""

    __slots__ = ()


__all__ = ["INotification"]
