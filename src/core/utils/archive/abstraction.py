"""Base types for :mod:`utils.archive`."""

from __future__ import annotations

from core.utils.abstraction import IUtility


class IArchiveUtility(IUtility):
    """Marker for ZIP/tar introspection helpers under :mod:`utils.archive`."""

    __slots__ = ()


__all__ = ["IArchiveUtility"]
