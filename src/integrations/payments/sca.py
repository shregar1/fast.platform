"""Strong Customer Authentication (SCA) / 3DS — optional gateway extension.

Implement :class:`IStrongCustomerAuthenticationGateway` alongside :class:`~fast_payments.base.IPaymentGateway`
when the PSP supports redirect or in-app 3DS challenges (Stripe PaymentIntent, Adyen, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Protocol, runtime_checkable


@dataclass
class SCAChallengeResult:
    """Outcome of initiating a payment that may require 3DS."""

    status: str
    """e.g. ``requires_action``, ``requires_payment_method``, ``succeeded``."""

    client_secret: Optional[str] = None
    next_action_url: Optional[str] = None
    payment_id: Optional[str] = None
    raw: Dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class IStrongCustomerAuthenticationGateway(Protocol):
    """Optional methods for gateways that expose 3DS / SCA flows.

    Apps should use ``isinstance(gw, IStrongCustomerAuthenticationGateway)`` before calling.
    """

    async def initiate_sca_payment(
        self,
        amount: int,
        currency: str,
        *,
        return_url: str,
        customer: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SCAChallengeResult:
        """Create or update a payment object that may return ``requires_action`` for 3DS."""
        ...

    async def complete_sca(
        self,
        payment_id: str,
        *,
        payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Complete after redirect or JS challenge (provider-specific *payload*)."""
        ...
