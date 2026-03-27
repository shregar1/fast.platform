"""tenancy package abstractions."""

from __future__ import annotations

from abc import ABC


class ITenancy(ABC):
    """Marker base for concrete types in the ``tenancy`` package."""

    __slots__ = ()


__all__ = ["ITenancy"]
