"""Retry jitter behavior for webhook delivery."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.messaging.webhooks.abstraction import IWebhookTests
from webhooks.delivery import RetryPolicy, deliver_webhook


class TestDeliveryJitter(IWebhookTests):
    @pytest.mark.asyncio
    async def test_jitter_scales_sleep(self, monkeypatch):
        sleeps: list[float] = []

        async def capture_sleep(seconds: float) -> None:
            sleeps.append(seconds)

        monkeypatch.setattr("webhooks.delivery.asyncio.sleep", capture_sleep)
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "err"
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.post = AsyncMock(return_value=mock_response)
        with patch("webhooks.delivery.httpx.AsyncClient", return_value=mock_client):
            with patch("webhooks.delivery.random.uniform", return_value=1.5):
                await deliver_webhook(
                    "https://example.com/hook",
                    b"{}",
                    retry_policy=RetryPolicy(
                        max_attempts=2,
                        initial_delay_seconds=1.0,
                        backoff_factor=2.0,
                        jitter_ratio=0.2,
                    ),
                )
        assert len(sleeps) == 1
        assert sleeps[0] == pytest.approx(1.5)
