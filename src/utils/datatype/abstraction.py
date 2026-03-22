"""Base types for :mod:`utils.datatype`."""

from __future__ import annotations

from utils.abstraction import IUtility


class IDatatype(IUtility):
    """Marker for primitive coercion helpers under :mod:`utils.datatype`."""

    __slots__ = ()


__all__ = ["IDatatype"]
