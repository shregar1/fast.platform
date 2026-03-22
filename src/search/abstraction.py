"""search package abstractions."""

from __future__ import annotations

from abc import ABC


class ISearch(ABC):
    """Marker base for concrete types in the ``search`` package."""

    __slots__ = ()


__all__ = ["ISearch"]
