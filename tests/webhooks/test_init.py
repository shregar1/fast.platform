"""Tests for fast_webhooks."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest


def test_imports():
    from fast_webhooks import (
        compute_signature,
        verify_signature,
        deliver_webhook,
        RetryPolicy,
        require_webhook_signature,
    )
    assert compute_signature(b"test", "secret") is not None
    assert require_webhook_signature(secret="x") is not None


def test_verify_roundtrip():
    from fast_webhooks import compute_signature, verify_signature, signature_header_value

    payload = b'{"event":"test"}'
    secret = "sk_test"
    header = signature_header_value(payload, secret)
    assert verify_signature(payload, header, secret) is True
    assert verify_signature(payload, "sha256=wrong", secret) is False
    assert verify_signature(payload, "not-prefixed", secret) is False


def test_compute_signature_rejects_unknown_digest():
    from fast_webhooks import compute_signature

    with pytest.raises(ValueError, match="Unsupported HMAC"):
        compute_signature(b"x", "s", algorithm="not_a_real_digest")


@pytest.mark.asyncio
async def test_deliver_webhook_success_with_signature_and_non_retryable_error():
    from fast_webhooks.delivery import RetryPolicy, deliver_webhook

    mock_response_ok = MagicMock(status_code=200, text="ok")
    mock_response_bad = MagicMock(status_code=400, text="bad request")

    with patch("fast_webhooks.delivery.httpx.AsyncClient") as mock_client:
        inst = mock_client.return_value.__aenter__.return_value
        inst.post = AsyncMock(side_effect=[mock_response_ok])

        code, err = await deliver_webhook("http://example/hook", b"{}", secret="sec")
        assert code == 200
        assert err is None
        call_kw = inst.post.call_args
        assert "X-Webhook-Signature" in call_kw[1]["headers"]

    with patch("fast_webhooks.delivery.httpx.AsyncClient") as mock_client:
        inst = mock_client.return_value.__aenter__.return_value
        inst.post = AsyncMock(return_value=mock_response_bad)
        code, err = await deliver_webhook(
            "http://example/hook",
            b"{}",
            retry_policy=RetryPolicy(max_attempts=1),
        )
        assert code == 400
        assert err is not None


@pytest.mark.asyncio
async def test_deliver_webhook_records_transport_error():
    from fast_webhooks.delivery import RetryPolicy, deliver_webhook

    with patch("fast_webhooks.delivery.httpx.AsyncClient") as mock_client:
        inst = mock_client.return_value.__aenter__.return_value
        inst.post = AsyncMock(side_effect=OSError("down"))
        code, err = await deliver_webhook(
            "http://example/hook",
            b"{}",
            retry_policy=RetryPolicy(max_attempts=1),
        )
        assert code == 0
        assert err is not None


def test_deliver_webhook_sync():
    from fast_webhooks.delivery import deliver_webhook_sync

    mock_response = MagicMock(status_code=201, text="created")
    with patch("fast_webhooks.delivery.httpx.AsyncClient") as mock_client:
        inst = mock_client.return_value.__aenter__.return_value
        inst.post = AsyncMock(return_value=mock_response)
        code, err = deliver_webhook_sync("http://example/hook", b"{}")
    assert code == 201
    assert err is None


@pytest.mark.asyncio
async def test_resolve_secret_async_callable():
    from fast_webhooks.fastapi_deps import _resolve_secret

    async def async_secret() -> str:
        return "from-async"

    assert await _resolve_secret(async_secret) == "from-async"
