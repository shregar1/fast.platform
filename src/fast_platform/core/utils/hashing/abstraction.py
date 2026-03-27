"""Base types for :mod:`utils.hashing`."""

from __future__ import annotations

from ..abstraction import IUtility


class IHashingUtility(IUtility):
    """Marker for HMAC / streaming hash helpers under :mod:`utils.hashing`."""

    __slots__ = ()


__all__ = ["IHashingUtility"]
