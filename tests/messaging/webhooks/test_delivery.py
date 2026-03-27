"""Tests for outbound webhook delivery (mocked HTTP)."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from tests.messaging.webhooks.abstraction import IWebhookTests
from fast_platform.messaging.webhooks import RetryPolicy, deliver_webhook


class TestDelivery(IWebhookTests):
    """Represents the TestDelivery class."""

    @pytest.mark.asyncio
    async def test_deliver_webhook_success(self, monkeypatch):
        """Execute test_deliver_webhook_success operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """

        class _Ok:
            """Represents the _Ok class."""

            status_code = 200
            text = ""

        mock_post = AsyncMock(return_value=_Ok())
        inner = MagicMock(post=mock_post)
        cm = MagicMock()
        cm.__aenter__ = AsyncMock(return_value=inner)
        cm.__aexit__ = AsyncMock(return_value=None)
        monkeypatch.setattr("fast_platform.messaging.webhooks.delivery.httpx.AsyncClient", lambda *a, **k: cm)
        code, err = await deliver_webhook(
            "https://example.com/hook", b'{"ok":true}', retry_policy=RetryPolicy(max_attempts=1)
        )
        assert code == 200
        assert err is None

    @pytest.mark.asyncio
    async def test_deliver_webhook_nonretryable_400(self, monkeypatch):
        """Execute test_deliver_webhook_nonretryable_400 operation.

        Args:
            monkeypatch: The monkeypatch parameter.

        Returns:
            The result of the operation.
        """

        class _Bad:
            """Represents the _Bad class."""

            status_code = 400
            text = "bad"

        mock_post = AsyncMock(return_value=_Bad())
        inner = MagicMock(post=mock_post)
        cm = MagicMock()
        cm.__aenter__ = AsyncMock(return_value=inner)
        cm.__aexit__ = AsyncMock(return_value=None)
        monkeypatch.setattr("fast_platform.messaging.webhooks.delivery.httpx.AsyncClient", lambda *a, **k: cm)
        code, err = await deliver_webhook(
            "https://example.com/hook", b"{}", retry_policy=RetryPolicy(max_attempts=1)
        )
        assert code == 400
        assert err is not None
