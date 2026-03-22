from __future__ import annotations

"""Test-suite markers for ``utils`` (mirrors ``src/utils/``)."""

from abc import ABC

from tests.core.abstraction import ICoreSuite


class IUtilsTests(ICoreSuite, ABC):
    """Marker base for test classes covering :mod:`utils`."""

    __slots__ = ()


__all__ = ["IUtilsTests"]
