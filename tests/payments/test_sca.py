"""Tests for SCA / 3DS gateway protocol."""

import asyncio
from typing import Any, Dict, Optional

from payments.sca import IStrongCustomerAuthenticationGateway, SCAChallengeResult


class StubSCAGateway:
    async def initiate_sca_payment(
        self,
        amount: int,
        currency: str,
        *,
        return_url: str,
        customer: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SCAChallengeResult:
        return SCAChallengeResult(
            status="requires_action",
            client_secret="sec_test",
            payment_id="pi_x",
        )

    async def complete_sca(
        self,
        payment_id: str,
        *,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        return {"id": payment_id, "status": "succeeded"}


def test_sca_gateway_isinstance_protocol():
    g = StubSCAGateway()
    assert isinstance(g, IStrongCustomerAuthenticationGateway)


def test_stub_sca_flow():
    async def run():
        g = StubSCAGateway()
        r = await g.initiate_sca_payment(1000, "usd", return_url="https://app/cb")
        assert r.status == "requires_action"
        out = await g.complete_sca("pi_x")
        assert out["status"] == "succeeded"

    asyncio.run(run())
