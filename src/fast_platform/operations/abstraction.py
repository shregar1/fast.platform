"""operations package abstractions."""

from __future__ import annotations

from abc import ABC


class IOperations(ABC):
    """Marker base for concrete types in the ``operations`` package."""

    __slots__ = ()


__all__ = ["IOperations"]
