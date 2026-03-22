from __future__ import annotations

"""Test-suite markers for ``service`` (mirrors ``src/service/``)."""

from abc import ABC

from tests.core.abstraction import ICoreSuite


class IServiceTests(ICoreSuite, ABC):
    """Marker base for test classes covering :mod:`service`."""

    __slots__ = ()


__all__ = ["IServiceTests"]
