from __future__ import annotations

"""Tests for ``observability.abstraction``."""
from abc import ABC

from observability.abstraction import IObservability
from tests.operations.observability.abstraction import IObservabilityTests


class TestIObservability(IObservabilityTests):
    def test_is_abstract_base(self) -> None:
        assert issubclass(IObservability, ABC)
