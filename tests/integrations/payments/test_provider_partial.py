"""Module test_provider_partial.py."""

from __future__ import annotations

"""Tests for partial capture/refund on IPaymentGateway / IProvider."""
import asyncio
from typing import Any, Dict, Optional

from fast_platform.integrations.payments.abstraction import IPaymentGateway, IProvider
from tests.integrations.payments.abstraction import IPaymentsTests


class TestProviderPartial(IPaymentsTests):
    """Represents the TestProviderPartial class."""

    class StubGateway(IPaymentGateway):
        """Represents the StubGateway class."""

        name = "stub"

        def __init__(self) -> None:
            """Execute __init__ operation."""
            self.captures: list[tuple[str, Optional[int]]] = []
            self.refunds: list[tuple[str, Optional[int]]] = []

        async def create_checkout_session(self, *args: Any, **kwargs: Any):
            """Execute create_checkout_session operation.

            Returns:
                The result of the operation.
            """
            raise NotImplementedError

        async def capture_payment(
            self,
            payment_id: str,
            amount: Optional[int] = None,
            *,
            metadata: Optional[Dict[str, Any]] = None,
        ) -> Dict[str, Any]:
            """Execute capture_payment operation.

            Args:
                payment_id: The payment_id parameter.
                amount: The amount parameter.
                metadata: The metadata parameter.

            Returns:
                The result of the operation.
            """
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
            """Execute refund_payment operation.

            Args:
                payment_id: The payment_id parameter.
                amount: The amount parameter.
                reason: The reason parameter.
                metadata: The metadata parameter.

            Returns:
                The result of the operation.
            """
            self.refunds.append((payment_id, amount))
            return {"id": payment_id, "amount": amount}

        async def verify_webhook(self, payload: bytes, headers: Dict[str, str]) -> Dict[str, Any]:
            """Execute verify_webhook operation.

            Args:
                payload: The payload parameter.
                headers: The headers parameter.

            Returns:
                The result of the operation.
            """
            return {}

    def test_iprovider_is_alias(self) -> None:
        """Execute test_iprovider_is_alias operation.

        Returns:
            The result of the operation.
        """
        assert IProvider is IPaymentGateway

    def test_partial_capture_and_refund(self) -> None:
        """Execute test_partial_capture_and_refund operation.

        Returns:
            The result of the operation.
        """

        async def run() -> None:
            """Execute run operation.

            Returns:
                The result of the operation.
            """
            g = self.StubGateway()
            await g.capture_payment("pi_1", 500)
            await g.capture_payment("pi_2", None)
            await g.refund_payment("pi_1", 100)
            await g.refund_payment("pi_2", None)
            assert g.captures == [("pi_1", 500), ("pi_2", None)]
            assert g.refunds == [("pi_1", 100), ("pi_2", None)]

        asyncio.run(run())
