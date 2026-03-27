"""Module test_abstraction.py."""

from __future__ import annotations

"""Tests for ``operations.observability.abstraction``."""
from abc import ABC

from fast_platform.operations.observability.abstraction import IObservability
from tests.operations.observability.abstraction import IObservabilityTests


class TestIObservability(IObservabilityTests):
    """Represents the TestIObservability class."""

    def test_is_abstract_base(self) -> None:
        """Execute test_is_abstract_base operation.

        Returns:
            The result of the operation.
        """
        assert issubclass(IObservability, ABC)
