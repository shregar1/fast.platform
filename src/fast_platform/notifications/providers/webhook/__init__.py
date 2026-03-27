"""Generic Webhook Integration.

Send notifications to any HTTP endpoint.
"""

from .client import WebhookClient, WebhookSignature

__all__ = ["WebhookClient", "WebhookSignature"]
