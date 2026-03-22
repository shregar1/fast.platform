"""Tests for subscription lifecycle event enum."""

from fast_payments.subscription_events import (
    SubscriptionLifecycleEvent,
    parse_subscription_lifecycle_event,
)


def test_parse_known_event():
    assert parse_subscription_lifecycle_event("invoice.paid") == SubscriptionLifecycleEvent.INVOICE_PAID
    assert (
        parse_subscription_lifecycle_event("customer.subscription.deleted")
        == SubscriptionLifecycleEvent.CUSTOMER_SUBSCRIPTION_DELETED
    )


def test_parse_unknown_returns_none():
    assert parse_subscription_lifecycle_event("unknown.event") is None


def test_enum_values_are_stripe_style():
    assert SubscriptionLifecycleEvent.INVOICE_PAID.value == "invoice.paid"
