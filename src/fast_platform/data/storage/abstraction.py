"""storage package abstractions."""

from __future__ import annotations

from abc import ABC


class IStorage(ABC):
    """Marker base for concrete types in the ``storage`` package."""

    __slots__ = ()


__all__ = ["IStorage"]
