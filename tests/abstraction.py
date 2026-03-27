"""Module abstraction.py."""

from __future__ import annotations

"""
Root test-suite marker: all package-level ``I*Tests`` bases inherit :class:`ITest`.

Mirrors the ``I*`` abstraction pattern used under ``src/``.
"""

from abc import ABC


class ITest(ABC):
    """Marker base for pytest classes under ``tests/``."""

    __slots__ = ()


__all__ = ["ITest"]
