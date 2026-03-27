"""Module test_public_api.py."""

from __future__ import annotations

"""Tests for ``observability`` public re-exports."""
import fast_platform.operations.observability as observability

from tests.operations.observability.abstraction import IObservabilityTests


class TestObservabilityPublicApi(IObservabilityTests):
    """Represents the TestObservabilityPublicApi class."""

    def test_all_matches_documented_exports(self) -> None:
        """Execute test_all_matches_documented_exports operation.

        Returns:
            The result of the operation.
        """
        expected = {
            "StructuredLogger",
            "configure_datadog",
            "configure_otel",
            "Metrics",
            "MetricsMiddleware",
            "Tracer",
            "TracingMiddleware",
            "AuditLog",
            "audit_log",
        }
        assert set(observability.__all__) == expected

    def test_importable_symbols(self) -> None:
        """Execute test_importable_symbols operation.

        Returns:
            The result of the operation.
        """
        for name in observability.__all__:
            assert hasattr(observability, name)
            assert getattr(observability, name) is not None
