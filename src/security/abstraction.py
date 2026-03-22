"""Base types for :mod:`security`."""

from __future__ import annotations

from abc import ABC


class ISecurity(ABC):
    """Base class for security helpers (encryption, API keys, webhooks)."""

    __slots__ = ()


__all__ = ["ISecurity"]
