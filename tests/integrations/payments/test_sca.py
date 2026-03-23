from __future__ import annotations

"""Tests for SCA / 3DS gateway protocol."""
import asyncio
from typing import Any, Dict, Optional

from integrations.payments.sca import IStrongCustomerAuthenticationGateway, SCAChallengeResult
from tests.integrations.payments.abstraction import IPaymentsTests


class TestSca(IPaymentsTests):
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
                status="requires_action", client_secret="sec_test", payment_id="pi_x"
            )

        async def complete_sca(
            self, payment_id: str, *, payload: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            return {"id": payment_id, "status": "succeeded"}

    def test_sca_gateway_isinstance_protocol(self) -> None:
        g = self.StubSCAGateway()
        assert isinstance(g, IStrongCustomerAuthenticationGateway)

    def test_stub_sca_flow(self) -> None:
        async def run() -> None:
            g = self.StubSCAGateway()
            r = await g.initiate_sca_payment(1000, "usd", return_url="https://app/cb")
            assert r.status == "requires_action"
            out = await g.complete_sca("pi_x")
            assert out["status"] == "succeeded"

        asyncio.run(run())
