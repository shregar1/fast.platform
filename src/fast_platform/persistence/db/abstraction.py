"""db package abstractions."""

from __future__ import annotations

from abc import ABC


class IDatabase(ABC):
    """Marker base for concrete types in the ``db`` package."""

    __slots__ = ()


__all__ = ["IDatabase"]
