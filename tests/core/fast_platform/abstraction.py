from __future__ import annotations

"""Test-suite markers for ``fast_platform`` (mirrors ``src/fast_platform/``)."""

from abc import ABC

from tests.core.abstraction import ICoreSuite


class IFastPlatformTests(ICoreSuite, ABC):
    """Marker base for test classes covering :mod:`fast_platform`."""

    __slots__ = ()


__all__ = ["IFastPlatformTests"]
