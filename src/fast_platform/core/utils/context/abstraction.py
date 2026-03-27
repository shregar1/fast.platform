"""context package abstractions."""

from __future__ import annotations

from abc import ABC


class IContext(ABC):
    """Marker base for concrete types in the ``context`` package."""

    __slots__ = ()


__all__ = ["IContext"]
