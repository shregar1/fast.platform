"""Stripe integration."""

from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from functools import wraps


@dataclass
class PaymentIntent:
    """Stripe payment intent."""

    id: str
    amount: int
    currency: str
    status: str
    client_secret: Optional[str] = None
    metadata: Dict[str, str] = None


@dataclass
class Customer:
    """Stripe customer."""

    id: str
    email: Optional[str] = None
    name: Optional[str] = None
    metadata: Dict[str, str] = None


class StripeClient:
    """Stripe API client."""

    def __init__(self, api_key: Optional[str] = None):
        """Execute __init__ operation.

        Args:
            api_key: The api_key parameter.
        """
        self.api_key = api_key
        self._client = None

    def _get_client(self):
        """Execute _get_client operation.

        Returns:
            The result of the operation.
        """
        if self._client is None:
            try:
                import stripe

                stripe.api_key = self.api_key
                self._client = stripe
            except ImportError:
                raise ImportError("stripe package required for StripeClient")
        return self._client

    async def create_payment_intent(
        self,
        amount: int,
        currency: str = "usd",
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        automatic_payment_methods: bool = True,
    ) -> PaymentIntent:
        """Create a payment intent.

        Args:
            amount: Amount in smallest currency unit (cents)
            currency: Currency code
            customer_id: Optional customer ID
            metadata: Additional metadata

        """
        stripe = self._get_client()

        params = {
            "amount": amount,
            "currency": currency,
            "automatic_payment_methods": {"enabled": automatic_payment_methods},
        }

        if customer_id:
            params["customer"] = customer_id
        if metadata:
            params["metadata"] = metadata

        intent = stripe.PaymentIntent.create(**params)

        return PaymentIntent(
            id=intent.id,
            amount=intent.amount,
            currency=intent.currency,
            status=intent.status,
            client_secret=intent.client_secret,
            metadata=intent.metadata or {},
        )

    async def confirm_payment_intent(
        self, intent_id: str, payment_method: Optional[str] = None
    ) -> PaymentIntent:
        """Confirm a payment intent."""
        stripe = self._get_client()

        params = {}
        if payment_method:
            params["payment_method"] = payment_method

        intent = stripe.PaymentIntent.confirm(intent_id, **params)

        return PaymentIntent(
            id=intent.id,
            amount=intent.amount,
            currency=intent.currency,
            status=intent.status,
            client_secret=intent.client_secret,
            metadata=intent.metadata or {},
        )

    async def create_customer(
        self,
        email: Optional[str] = None,
        name: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
    ) -> Customer:
        """Create a customer."""
        stripe = self._get_client()

        params = {}
        if email:
            params["email"] = email
        if name:
            params["name"] = name
        if metadata:
            params["metadata"] = metadata

        customer = stripe.Customer.create(**params)

        return Customer(
            id=customer.id,
            email=customer.email,
            name=customer.name,
            metadata=customer.metadata or {},
        )

    async def create_subscription(
        self, customer_id: str, price_id: str, metadata: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Create a subscription."""
        stripe = self._get_client()

        params = {"customer": customer_id, "items": [{"price": price_id}]}
        if metadata:
            params["metadata"] = metadata

        return stripe.Subscription.create(**params)

    def verify_webhook_signature(
        self, payload: bytes, signature: str, webhook_secret: str
    ) -> Dict[str, Any]:
        """Verify Stripe webhook signature."""
        stripe = self._get_client()

        try:
            event = stripe.Webhook.construct_event(payload, signature, webhook_secret)
            return event
        except Exception as e:
            raise ValueError(f"Invalid webhook signature: {e}")


def stripe_webhook(secret: str, event_types: Optional[list] = None):
    """Decorator for Stripe webhook handlers.

    Args:
        secret: Webhook signing secret
        event_types: List of event types to handle

    """

    def decorator(func: Callable):
        """Execute decorator operation.

        Args:
            func: The func parameter.

        Returns:
            The result of the operation.
        """
        func._is_stripe_webhook = True
        func._stripe_webhook_secret = secret
        func._stripe_event_types = event_types or []

        @wraps(func)
        async def wrapper(payload: bytes, signature: str, **kwargs):
            """Execute wrapper operation.

            Args:
                payload: The payload parameter.
                signature: The signature parameter.

            Returns:
                The result of the operation.
            """
            client = StripeClient()
            event = client.verify_webhook_signature(payload, signature, secret)

            if event_types and event["type"] not in event_types:
                return {"status": "ignored"}

            return await func(event, **kwargs)

        return wrapper

    return decorator
