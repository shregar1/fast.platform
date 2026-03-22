from __future__ import annotations
from tests.operations.abstraction import IOperationsSuite
"""Test-suite markers for ``observability`` (mirrors ``src/observability/``)."""


from abc import ABC



class IObservabilityTests(IOperationsSuite, ABC):
    """Marker base for test classes covering :mod:`observability`."""

    __slots__ = ()


__all__ = ["IObservabilityTests"]
