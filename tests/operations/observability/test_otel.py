from __future__ import annotations
"""Tests for ``observability.otel``."""
from tests.operations.observability.abstraction import IObservabilityTests



from unittest.mock import MagicMock, patch

from fastapi import FastAPI

from observability.otel import configure_otel


class TestConfigureOtel(IObservabilityTests):
    @patch("observability.otel.TelemetryConfiguration")
    def test_no_op_when_disabled(self, mock_tc: MagicMock) -> None:
        mock_tc.return_value.get_config.return_value = MagicMock(enabled=False)
        app = FastAPI()
        configure_otel(app)
