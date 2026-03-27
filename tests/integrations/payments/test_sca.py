"""Module test_sca.py."""

from __future__ import annotations

"""Tests for SCA / 3DS gateway protocol."""
import asyncio
from typing import Any, Dict, Optional

from fast_platform.integrations.payments.sca import IStrongCustomerAuthenticationGateway, SCAChallengeResult
from tests.integrations.payments.abstraction import IPaymentsTests


class TestSca(IPaymentsTests):
    """Represents the TestSca class."""

    class StubSCAGateway:
        """Represents the StubSCAGateway class."""

        async def initiate_sca_payment(
            self,
            amount: int,
            currency: str,
            *,
            return_url: str,
            customer: Optional[Dict[str, Any]] = None,
            metadata: Optional[Dict[str, Any]] = None,
        ) -> SCAChallengeResult:
            """Execute initiate_sca_payment operation.

            Args:
                amount: The amount parameter.
                currency: The currency parameter.
                return_url: The return_url parameter.
                customer: The customer parameter.
                metadata: The metadata parameter.

            Returns:
                The result of the operation.
            """
            return SCAChallengeResult(
                status="requires_action", client_secret="sec_test", payment_id="pi_x"
            )

        async def complete_sca(
            self, payment_id: str, *, payload: Optional[Dict[str, Any]] = None
        ) -> Dict[str, Any]:
            """Execute complete_sca operation.

            Args:
                payment_id: The payment_id parameter.
                payload: The payload parameter.

            Returns:
                The result of the operation.
            """
            return {"id": payment_id, "status": "succeeded"}

    def test_sca_gateway_isinstance_protocol(self) -> None:
        """Execute test_sca_gateway_isinstance_protocol operation.

        Returns:
            The result of the operation.
        """
        g = self.StubSCAGateway()
        assert isinstance(g, IStrongCustomerAuthenticationGateway)

    def test_stub_sca_flow(self) -> None:
        """Execute test_stub_sca_flow operation.

        Returns:
            The result of the operation.
        """

        async def run() -> None:
            """Execute run operation.

            Returns:
                The result of the operation.
            """
            g = self.StubSCAGateway()
            r = await g.initiate_sca_payment(1000, "usd", return_url="https://app/cb")
            assert r.status == "requires_action"
            out = await g.complete_sca("pi_x")
            assert out["status"] == "succeeded"

        asyncio.run(run())
