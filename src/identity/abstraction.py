"""identity package abstractions."""

from __future__ import annotations

from abc import ABC


class IIdentity(ABC):
    """Marker base for concrete types in the ``identity`` package."""

    __slots__ = ()


__all__ = ["IIdentity"]
