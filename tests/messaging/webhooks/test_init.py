"""Tests for webhooks."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.messaging.webhooks.abstraction import IWebhookTests


class TestInit(IWebhookTests):
    def test_imports(self):
        from webhooks import (
            compute_signature,
            require_webhook_signature,
        )

        assert compute_signature(b"test", "secret") is not None
        assert require_webhook_signature(secret="x") is not None

    def test_verify_roundtrip(self):
        from webhooks import signature_header_value, verify_signature

        payload = b'{"event":"test"}'
        secret = "sk_test"
        header = signature_header_value(payload, secret)
        assert verify_signature(payload, header, secret) is True
        assert verify_signature(payload, "sha256=wrong", secret) is False
        assert verify_signature(payload, "not-prefixed", secret) is False

    def test_compute_signature_rejects_unknown_digest(self):
        from webhooks import compute_signature

        with pytest.raises(ValueError, match="Unsupported HMAC"):
            compute_signature(b"x", "s", algorithm="not_a_real_digest")

    @pytest.mark.asyncio
    async def test_deliver_webhook_success_with_signature_and_non_retryable_error(self):
        from webhooks.delivery import RetryPolicy, deliver_webhook

        mock_response_ok = MagicMock(status_code=200, text="ok")
        mock_response_bad = MagicMock(status_code=400, text="bad request")
        with patch("webhooks.delivery.httpx.AsyncClient") as mock_client:
            inst = mock_client.return_value.__aenter__.return_value
            inst.post = AsyncMock(side_effect=[mock_response_ok])
            code, err = await deliver_webhook("http://example/hook", b"{}", secret="sec")
            assert code == 200
            assert err is None
            call_kw = inst.post.call_args
            assert "X-Webhook-Signature" in call_kw[1]["headers"]
        with patch("webhooks.delivery.httpx.AsyncClient") as mock_client:
            inst = mock_client.return_value.__aenter__.return_value
            inst.post = AsyncMock(return_value=mock_response_bad)
            code, err = await deliver_webhook(
                "http://example/hook", b"{}", retry_policy=RetryPolicy(max_attempts=1)
            )
            assert code == 400
            assert err is not None

    @pytest.mark.asyncio
    async def test_deliver_webhook_records_transport_error(self):
        from webhooks.delivery import RetryPolicy, deliver_webhook

        with patch("webhooks.delivery.httpx.AsyncClient") as mock_client:
            inst = mock_client.return_value.__aenter__.return_value
            inst.post = AsyncMock(side_effect=OSError("down"))
            code, err = await deliver_webhook(
                "http://example/hook", b"{}", retry_policy=RetryPolicy(max_attempts=1)
            )
            assert code == 0
            assert err is not None

    def test_deliver_webhook_sync(self):
        from webhooks.delivery import deliver_webhook_sync

        mock_response = MagicMock(status_code=201, text="created")
        with patch("webhooks.delivery.httpx.AsyncClient") as mock_client:
            inst = mock_client.return_value.__aenter__.return_value
            inst.post = AsyncMock(return_value=mock_response)
            code, err = deliver_webhook_sync("http://example/hook", b"{}")
        assert code == 201
        assert err is None

    @pytest.mark.asyncio
    async def test_resolve_secret_async_callable(self):
        from webhooks.fastapi_deps import _resolve_secret

        async def async_secret() -> str:
            return "from-async"

        assert await _resolve_secret(async_secret) == "from-async"
