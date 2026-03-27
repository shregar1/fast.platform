"""core package abstractions."""

from __future__ import annotations

from abc import ABC


class ICore(ABC):
    """Marker base for concrete types in the ``core`` package."""

    __slots__ = ()


__all__ = ["ICore"]
