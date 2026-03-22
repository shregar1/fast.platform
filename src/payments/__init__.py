"""
fast_payments – Payments config and base abstractions for FastMVC.
"""

from configuration.payments import PaymentsConfiguration
from dtos.payments import (
    LinkConfigDTO,
    PaymentsConfigurationDTO,
    PaypalConfigDTO,
    PayUConfigDTO,
    RazorpayConfigDTO,
    StripeConfigDTO,
)

from .abstraction import CheckoutSession, IPaymentGateway, IProvider
from .reconciliation import (
    ReconciliationLineItem,
    ReconciliationMismatchKind,
    ReconciliationReport,
    reconciliation_report_to_csv,
)
from .sca import IStrongCustomerAuthenticationGateway, SCAChallengeResult
from .subscription_events import SubscriptionLifecycleEvent, parse_subscription_lifecycle_event
from .webhook_idempotency import InMemoryWebhookIdempotencyStore, WebhookIdempotencyStore

__version__ = "0.3.0"

__all__ = [
    "CheckoutSession",
    "IPaymentGateway",
    "IProvider",
    "IStrongCustomerAuthenticationGateway",
    "InMemoryWebhookIdempotencyStore",
    "PaymentsConfiguration",
    "PaymentsConfigurationDTO",
    "ReconciliationLineItem",
    "ReconciliationMismatchKind",
    "ReconciliationReport",
    "SCAChallengeResult",
    "StripeConfigDTO",
    "RazorpayConfigDTO",
    "PaypalConfigDTO",
    "PayUConfigDTO",
    "LinkConfigDTO",
    "SubscriptionLifecycleEvent",
    "WebhookIdempotencyStore",
    "parse_subscription_lifecycle_event",
    "reconciliation_report_to_csv",
]
