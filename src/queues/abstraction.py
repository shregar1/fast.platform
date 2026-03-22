"""queues package abstractions."""

from __future__ import annotations

from abc import ABC


class IQueue(ABC):
    """Marker base for concrete types in the ``queues`` package."""

    __slots__ = ()


__all__ = ["IQueue"]
