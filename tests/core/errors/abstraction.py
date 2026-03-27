"""Module abstraction.py."""

from __future__ import annotations

"""Test-suite markers for ``errors`` (mirrors ``src/errors/``)."""

from abc import ABC

from tests.core.abstraction import ICoreSuite


class IErrorsTests(ICoreSuite, ABC):
    """Marker base for test classes covering :mod:`errors`."""

    __slots__ = ()


__all__ = ["IErrorsTests"]
