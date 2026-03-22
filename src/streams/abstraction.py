"""streams package abstractions."""

from __future__ import annotations

from abc import ABC


class IStreams(ABC):
    """Marker base for concrete types in the ``streams`` package."""

    __slots__ = ()


__all__ = ["IStreams"]
