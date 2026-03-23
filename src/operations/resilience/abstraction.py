"""resilience package abstractions."""

from __future__ import annotations

from abc import ABC


class IResilience(ABC):
    """Marker base for concrete types in the ``resilience`` package."""

    __slots__ = ()


__all__ = ["IResilience"]
