"""FastAPI dependencies for inbound webhook HMAC verification.

Requires FastAPI (``pip install fast_webhooks[fastapi]``).
"""

import asyncio
from typing import Any, Awaitable, Callable, Union

from .signing import verify_signature

SecretSource = Union[str, Callable[[], str], Callable[[], Awaitable[str]]]


async def _resolve_secret(secret: SecretSource) -> str:
    """Execute _resolve_secret operation.

    Args:
        secret: The secret parameter.

    Returns:
        The result of the operation.
    """
    if isinstance(secret, str):
        return secret
    out = secret()
    if asyncio.iscoroutine(out):
        return str(await out)
    return str(out)


def require_webhook_signature(
    *,
    secret: SecretSource,
    header_name: str = "X-Webhook-Signature",
    prefix: str = "sha256=",
    algorithm: str = "sha256",
    status_code: int = 401,
    detail_missing: str = "Missing webhook signature",
    detail_invalid: str = "Invalid webhook signature",
) -> Any:
    """Build a FastAPI dependency that reads the raw request body, verifies the
    HMAC signature header (Stripe-style ``sha256=<hex>`` by default), and
    returns the verified body bytes.

    Use with ``Depends(...)`` on your inbound webhook route. The body is only
    validated once; Starlette caches ``request.body()`` for the request.

    Example::

        @app.post("/webhooks/inbound")
        async def handle(
            raw: Annotated[bytes, Depends(require_webhook_signature(secret=settings.webhook_secret))],
        ):
            data = json.loads(raw)

    Parameters
    ----------
    secret
        Shared secret string, or a callable (sync or async) that returns it
        (e.g. read from settings/env per request).
    header_name
        Request header containing the signature (case-insensitive lookup).
    prefix
        Expected prefix before the hex digest (e.g. ``sha256=``).
    algorithm
        Hash algorithm name passed to :func:`verify_signature`.
    status_code
        HTTP status when the header is missing or invalid (default 401).
    detail_missing / detail_invalid
        Error detail strings for FastAPI ``HTTPException``.

    """
    try:
        from fastapi import HTTPException, Request
    except ImportError as e:  # pragma: no cover - import guard
        raise RuntimeError(
            "require_webhook_signature requires FastAPI. Install: pip install fast_webhooks[fastapi]"
        ) from e

    async def _verify(request: Request) -> bytes:
        """Execute _verify operation.

        Args:
            request: The request parameter.

        Returns:
            The result of the operation.
        """
        body = await request.body()
        resolved = await _resolve_secret(secret)
        sig = request.headers.get(header_name)
        if not sig:
            raise HTTPException(status_code=status_code, detail=detail_missing)
        if not verify_signature(body, sig, resolved, prefix=prefix, algorithm=algorithm):
            raise HTTPException(status_code=status_code, detail=detail_invalid)
        return body

    return _verify


__all__ = ["require_webhook_signature", "SecretSource"]
