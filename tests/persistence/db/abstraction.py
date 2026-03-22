from __future__ import annotations

from tests.persistence.abstraction import IPersistenceSuite

"""Test-suite markers for ``db`` (mirrors ``src/db/``)."""


from abc import ABC


class IDatabaseTests(IPersistenceSuite, ABC):
    """Marker base for test classes covering :mod:`db`."""

    __slots__ = ()


__all__ = ["IDatabaseTests"]
