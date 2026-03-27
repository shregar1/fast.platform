"""Module test_otel.py."""

from __future__ import annotations

"""Tests for ``operations.observability.otel``."""
from unittest.mock import MagicMock, patch

from fastapi import FastAPI

from operations.observability.otel import configure_otel
from tests.operations.observability.abstraction import IObservabilityTests


class TestConfigureOtel(IObservabilityTests):
    """Represents the TestConfigureOtel class."""

    @patch("operations.observability.otel.TelemetryConfiguration")
    def test_no_op_when_disabled(self, mock_tc: MagicMock) -> None:
        """Execute test_no_op_when_disabled operation.

        Args:
            mock_tc: The mock_tc parameter.

        Returns:
            The result of the operation.
        """
        mock_tc.return_value.get_config.return_value = MagicMock(enabled=False)
        app = FastAPI()
        configure_otel(app)
