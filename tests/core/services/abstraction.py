from __future__ import annotations

"""Test-suite markers for ``services`` (mirrors ``src/services/``)."""

from abc import ABC

from tests.core.abstraction import ICoreSuite


class IServicesTests(ICoreSuite, ABC):
    """Marker base for test classes covering :mod:`services`."""

    __slots__ = ()


__all__ = ["IServicesTests"]
