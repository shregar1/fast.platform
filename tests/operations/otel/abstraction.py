"""Module abstraction.py."""

from __future__ import annotations

from tests.operations.abstraction import IOperationsSuite

"""Test-suite markers for ``otel`` (mirrors ``src/otel/``)."""


from abc import ABC


class IOtelTests(IOperationsSuite, ABC):
    """Marker base for test classes covering :mod:`otel`."""

    __slots__ = ()


__all__ = ["IOtelTests"]
