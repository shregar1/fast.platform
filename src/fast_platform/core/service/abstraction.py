"""Base types for :mod:`service`."""

from __future__ import annotations

from abc import ABC


class IService(ABC):
    """Base class for application services in :mod:`service`."""

    __slots__ = ()


__all__ = ["IService"]
