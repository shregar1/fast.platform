from __future__ import annotations
"""Tests for partial capture/refund on IPaymentGateway / IProvider."""
from tests.integrations.payments.abstraction import IPaymentsTests



import asyncio
from typing import Any, Dict, Optional

from payments.abstraction import IPaymentGateway, IProvider


class TestProviderPartial(IPaymentsTests):
    class StubGateway(IPaymentGateway):
        name = "stub"

        def __init__(self) -> None:
            self.captures: list[tuple[str, Optional[int]]] = []
            self.refunds: list[tuple[str, Optional[int]]] = []

        async def create_checkout_session(self, *args: Any, **kwargs: Any):
            raise NotImplementedError

        async def capture_payment(
            self,
            payment_id: str,
            amount: Optional[int] = None,
            *,
            metadata: Optional[Dict[str, Any]] = None,
        ) -> Dict[str, Any]:
            self.captures.append((payment_id, amount))
            return {"id": payment_id, "amount": amount}

        async def refund_payment(
            self,
            payment_id: str,
            amount: Optional[int] = None,
            reason: Optional[str] = None,
            *,
            metadata: Optional[Dict[str, Any]] = None,
        ) -> Dict[str, Any]:
            self.refunds.append((payment_id, amount))
            return {"id": payment_id, "amount": amount}

        async def verify_webhook(self, payload: bytes, headers: Dict[str, str]) -> Dict[str, Any]:
            return {}

    def test_iprovider_is_alias(self) -> None:
        assert IProvider is IPaymentGateway

    def test_partial_capture_and_refund(self) -> None:
        async def run() -> None:
            g = self.StubGateway()
            await g.capture_payment("pi_1", 500)
            await g.capture_payment("pi_2", None)
            await g.refund_payment("pi_1", 100)
            await g.refund_payment("pi_2", None)
            assert g.captures == [("pi_1", 500), ("pi_2", None)]
            assert g.refunds == [("pi_1", 100), ("pi_2", None)]

        asyncio.run(run())
