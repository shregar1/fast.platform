"""vectors package abstractions."""

from __future__ import annotations

from abc import ABC


class IVector(ABC):
    """Marker base for concrete types in the ``vectors`` package."""

    __slots__ = ()


__all__ = ["IVector"]
