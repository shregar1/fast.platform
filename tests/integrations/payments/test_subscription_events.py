from __future__ import annotations

"""Tests for subscription lifecycle event enum."""
from payments.subscription_events import (
    SubscriptionLifecycleEvent,
    parse_subscription_lifecycle_event,
)
from tests.integrations.payments.abstraction import IPaymentsTests


class TestSubscriptionEvents(IPaymentsTests):
    def test_parse_known_event(self) -> None:
        assert (
            parse_subscription_lifecycle_event("invoice.paid")
            == SubscriptionLifecycleEvent.INVOICE_PAID
        )
        assert (
            parse_subscription_lifecycle_event("customer.subscription.deleted")
            == SubscriptionLifecycleEvent.CUSTOMER_SUBSCRIPTION_DELETED
        )

    def test_parse_unknown_returns_none(self) -> None:
        assert parse_subscription_lifecycle_event("unknown.event") is None

    def test_enum_values_are_stripe_style(self) -> None:
        assert SubscriptionLifecycleEvent.INVOICE_PAID.value == "invoice.paid"
