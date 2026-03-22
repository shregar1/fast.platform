"""Base abstractions for payment gateways."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


class IPayments(ABC):
    """Marker base for concrete types in the ``payments`` package."""

    __slots__ = ()


@dataclass
class CheckoutSession:
    """Represents a generic checkout session."""

    id: str
    url: Optional[str] = None
    provider: Optional[str] = None
    raw: Dict[str, Any] | None = None


class IPaymentGateway(IPayments, ABC):
    """
    Base interface for payment gateway implementations.

    Amounts are in the smallest currency unit (cents, paisa, …) unless documented otherwise.

    For 3DS / SCA, optionally implement
    :class:`~fast_payments.sca.IStrongCustomerAuthenticationGateway` in the same concrete class.
    """

    name: str

    @abstractmethod
    async def create_checkout_session(
        self,
        amount: int,
        currency: str,
        customer: Dict[str, Any] | None = None,
        metadata: Dict[str, Any] | None = None,
    ) -> CheckoutSession:
        raise NotImplementedError

    @abstractmethod
    async def capture_payment(
        self,
        payment_id: str,
        amount: Optional[int] = None,
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Capture a previously authorized charge.

        * ``amount`` — partial capture when set; ``None`` captures the remaining authorized amount.
        """
        raise NotImplementedError

    @abstractmethod
    async def refund_payment(
        self,
        payment_id: str,
        amount: Optional[int] = None,
        reason: Optional[str] = None,
        *,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Refund a captured charge.

        * ``amount`` — partial refund when set; ``None`` refunds the full captured amount.
        """
        raise NotImplementedError

    @abstractmethod
    async def verify_webhook(
        self,
        payload: bytes,
        headers: Dict[str, str],
    ) -> Dict[str, Any]:
        raise NotImplementedError


# Alias used in docs and integrations (same contract as :class:`IPaymentGateway`).
IProvider = IPaymentGateway

__all__ = ["CheckoutSession", "IPaymentGateway", "IPayments", "IProvider"]
