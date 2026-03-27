"""Base types for :mod:`utils.optional_imports`."""

from __future__ import annotations

from ..abstraction import IUtility


class IOptionalImportsUtility(IUtility):
    """Marker for optional dependency resolution under :mod:`utils.optional_imports`."""

    __slots__ = ()


__all__ = ["IOptionalImportsUtility"]
