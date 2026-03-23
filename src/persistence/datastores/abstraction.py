"""datastores package abstractions."""

from __future__ import annotations

from abc import ABC


class IDatastores(ABC):
    """Marker base for concrete types in the ``datastores`` package."""

    __slots__ = ()


__all__ = ["IDatastores"]
