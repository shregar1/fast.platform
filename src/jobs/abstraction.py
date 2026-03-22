"""jobs package abstractions."""

from __future__ import annotations

from abc import ABC


class IJob(ABC):
    """Marker base for concrete types in the ``jobs`` package."""

    __slots__ = ()


__all__ = ["IJob"]
