"""Module abstraction.py."""

from __future__ import annotations

from tests.data_platform.abstraction import IDataPlatformSuite

"""Test-suite markers for ``vectors`` (mirrors ``src/vectors/``)."""


from abc import ABC


class IVectorTests(IDataPlatformSuite, ABC):
    """Marker base for test classes covering :mod:`vectors`."""

    __slots__ = ()


__all__ = ["IVectorTests"]
