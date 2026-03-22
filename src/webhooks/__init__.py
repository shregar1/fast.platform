"""
fast_webhooks – Webhook signing, retries, and outbound delivery for FastMVC.
"""

from .delivery import (
    RetryPolicy,
    deliver_webhook,
    deliver_webhook_sync,
)
from .fastapi_deps import require_webhook_signature
from .signing import (
    compute_signature,
    signature_header_value,
    verify_signature,
)

__version__ = "0.1.1"

__all__ = [
    "compute_signature",
    "verify_signature",
    "signature_header_value",
    "RetryPolicy",
    "deliver_webhook",
    "deliver_webhook_sync",
    "require_webhook_signature",
]
