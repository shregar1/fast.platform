from __future__ import annotations

from tests.operations.abstraction import IOperationsSuite

"""Test-suite markers for ``tenancy`` (mirrors ``src/tenancy/``)."""


from abc import ABC


class ITenancyTests(IOperationsSuite, ABC):
    """Marker base for test classes covering :mod:`tenancy`."""

    __slots__ = ()


__all__ = ["ITenancyTests"]
