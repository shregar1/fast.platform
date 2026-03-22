"""events package abstractions."""

from __future__ import annotations

from abc import ABC


class IEvents(ABC):
    """Marker base for concrete types in the ``events`` package."""

    __slots__ = ()


__all__ = ["IEvents"]
