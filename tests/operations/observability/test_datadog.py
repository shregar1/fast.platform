from __future__ import annotations

"""Tests for ``observability.datadog``."""
from unittest.mock import MagicMock, patch

from observability.datadog import configure_datadog
from tests.operations.observability.abstraction import IObservabilityTests


class TestConfigureDatadog(IObservabilityTests):
    @patch("observability.datadog.DatadogConfiguration")
    def test_skips_when_disabled(self, mock_cfg: MagicMock) -> None:
        mock_cfg.return_value.get_config.return_value = MagicMock(enabled=False)
        configure_datadog()

    @patch("observability.datadog.DatadogConfiguration")
    def test_sets_env_when_enabled(self, mock_dc: MagicMock) -> None:
        mock_dc.return_value.get_config.return_value = MagicMock(
            enabled=True,
            env="prod",
            service="api",
            version="1.0.0",
            agent_host="127.0.0.1",
            agent_port=8126,
        )
        fake_env: dict[str, str] = {}
        with patch("observability.datadog.os.environ", fake_env):
            configure_datadog()
        assert fake_env.get("DD_SERVICE") == "api"
        assert fake_env.get("DD_ENV") == "prod"
        assert fake_env.get("DD_AGENT_HOST") == "127.0.0.1"
        assert fake_env.get("DD_TRACE_AGENT_PORT") == "8126"
