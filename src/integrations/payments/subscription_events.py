"""
Normalized subscription / billing webhook event names (Stripe-style strings).

Use :func:`parse_subscription_lifecycle_event` to map raw provider ``type`` fields.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional


class SubscriptionLifecycleEvent(str, Enum):
    """Cross-provider normalized lifecycle events (values match common Stripe webhooks)."""

    INVOICE_PAID = "invoice.paid"
    INVOICE_PAYMENT_FAILED = "invoice.payment_failed"
    INVOICE_FINALIZED = "invoice.finalized"
    CUSTOMER_SUBSCRIPTION_CREATED = "customer.subscription.created"
    CUSTOMER_SUBSCRIPTION_UPDATED = "customer.subscription.updated"
    CUSTOMER_SUBSCRIPTION_DELETED = "customer.subscription.deleted"
    CUSTOMER_SUBSCRIPTION_PAUSED = "customer.subscription.paused"
    CUSTOMER_SUBSCRIPTION_RESUMED = "customer.subscription.resumed"
    PAYMENT_INTENT_SUCCEEDED = "payment_intent.succeeded"
    PAYMENT_INTENT_PAYMENT_FAILED = "payment_intent.payment_failed"
    CHARGE_DISPUTE_CREATED = "charge.dispute.created"
    CHARGE_REFUNDED = "charge.refunded"


def parse_subscription_lifecycle_event(raw_type: str) -> Optional[SubscriptionLifecycleEvent]:
    """
    Map a webhook ``type`` string to :class:`SubscriptionLifecycleEvent`, or ``None`` if unknown.
    """
    try:
        return SubscriptionLifecycleEvent(raw_type)
    except ValueError:
        return None
