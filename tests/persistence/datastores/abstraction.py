from __future__ import annotations
from tests.persistence.abstraction import IPersistenceSuite
"""Test-suite markers for ``datastores`` (mirrors ``src/datastores/``)."""


from abc import ABC



class IDatastoresTests(IPersistenceSuite, ABC):
    """Marker base for test classes covering :mod:`datastores`."""

    __slots__ = ()


__all__ = ["IDatastoresTests"]
