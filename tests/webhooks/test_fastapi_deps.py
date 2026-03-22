"""Tests for FastAPI inbound webhook signature dependency."""

from typing import Annotated

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from fast_webhooks import require_webhook_signature, signature_header_value


@pytest.fixture
def app_and_client():
    secret = "whsec_test"

    app = FastAPI()

    @app.post("/hook")
    async def inbound(
        raw: Annotated[bytes, Depends(require_webhook_signature(secret=secret))],
    ):
        return {"ok": True, "n": len(raw)}

    return app, secret, TestClient(app)


def test_dependency_accepts_valid_signature(app_and_client):
    app, secret, client = app_and_client
    payload = b'{"event":"ping"}'
    hdr = signature_header_value(payload, secret)
    r = client.post("/hook", content=payload, headers={"X-Webhook-Signature": hdr})
    assert r.status_code == 200
    assert r.json()["n"] == len(payload)


def test_dependency_rejects_missing_header(app_and_client):
    _, _, client = app_and_client
    r = client.post("/hook", content=b"{}")
    assert r.status_code == 401
    assert "Missing" in r.json()["detail"]


def test_dependency_rejects_bad_signature(app_and_client):
    _, _, client = app_and_client
    payload = b"{}"
    r = client.post(
        "/hook",
        content=payload,
        headers={"X-Webhook-Signature": "sha256=deadbeef"},
    )
    assert r.status_code == 401
    assert "Invalid" in r.json()["detail"]


def test_secret_async_callable():
    secret = "async-secret"

    async def get_secret() -> str:
        return secret

    app = FastAPI()

    @app.post("/h2")
    async def inbound2(
        raw: Annotated[bytes, Depends(require_webhook_signature(secret=get_secret))],
    ):
        return {"n": len(raw)}

    client = TestClient(app)
    payload = b"x"
    hdr = signature_header_value(payload, secret)
    r = client.post("/h2", content=payload, headers={"X-Webhook-Signature": hdr})
    assert r.status_code == 200
