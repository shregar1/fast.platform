"""Payment provider configuration DTOs."""

from typing import Literal, Optional

from pydantic import BaseModel


class StripeConfigDTO(BaseModel):
    """Stripe configuration."""

    enabled: bool = False
    api_key: Optional[str] = None
    webhook_secret: Optional[str] = None
    default_currency: str = "usd"


class RazorpayConfigDTO(BaseModel):
    """Razorpay configuration."""

    enabled: bool = False
    key_id: Optional[str] = None
    key_secret: Optional[str] = None
    default_currency: str = "INR"


class PaypalConfigDTO(BaseModel):
    """PayPal configuration."""

    enabled: bool = False
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    environment: Literal["sandbox", "live"] = "sandbox"


class PayUConfigDTO(BaseModel):
    """PayU configuration."""

    enabled: bool = False
    merchant_key: Optional[str] = None
    merchant_salt: Optional[str] = None
    environment: Literal["test", "production"] = "test"


class LinkConfigDTO(BaseModel):
    """Generic pay-by-link configuration."""

    enabled: bool = False
    base_url: Optional[str] = None
    api_key: Optional[str] = None


class PaymentsConfigurationDTO(BaseModel):
    """Aggregated configuration for all supported payment providers."""

    stripe: StripeConfigDTO = StripeConfigDTO()
    razorpay: RazorpayConfigDTO = RazorpayConfigDTO()
    paypal: PaypalConfigDTO = PaypalConfigDTO()
    payu: PayUConfigDTO = PayUConfigDTO()
    link: LinkConfigDTO = LinkConfigDTO()
