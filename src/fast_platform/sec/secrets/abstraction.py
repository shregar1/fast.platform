"""secrets package abstractions."""

from __future__ import annotations

from abc import ABC


class ISecrets(ABC):
    """Marker base for concrete types in the ``secrets`` package."""

    __slots__ = ()


__all__ = ["ISecrets"]
