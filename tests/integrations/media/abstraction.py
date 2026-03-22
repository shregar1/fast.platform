from __future__ import annotations
from tests.integrations.abstraction import IIntegrationsSuite
"""Test-suite markers for ``media`` (mirrors ``src/media/``)."""


from abc import ABC



class IFastMediaTests(IIntegrationsSuite, ABC):
    """Marker base for test classes covering :mod:`media`."""

    __slots__ = ()


__all__ = ["IFastMediaTests"]
