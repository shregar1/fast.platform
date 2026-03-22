"""analytics package abstractions."""

from __future__ import annotations

from abc import ABC


class IAnalytics(ABC):
    """Marker base for concrete types in the ``analytics`` package."""

    __slots__ = ()


__all__ = ["IAnalytics"]
