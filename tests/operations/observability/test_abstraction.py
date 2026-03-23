from __future__ import annotations

"""Tests for ``operations.observability.abstraction``."""
from abc import ABC

from operations.observability.abstraction import IObservability
from tests.operations.observability.abstraction import IObservabilityTests


class TestIObservability(IObservabilityTests):
    def test_is_abstract_base(self) -> None:
        assert issubclass(IObservability, ABC)
