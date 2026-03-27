"""Base types for :mod:`utils.idempotency`."""

from __future__ import annotations

from core.utils.abstraction import IUtility


class IIdempotencyUtility(IUtility):
    """Marker for stable JSON / digest idempotency helpers under :mod:`utils.idempotency`."""

    __slots__ = ()


__all__ = ["IIdempotencyUtility"]
