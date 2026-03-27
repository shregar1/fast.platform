"""Request correlation ID stored in a ContextVar (async-safe per task).

Set from HTTP middleware (e.g. fast_middleware.RequestIDMiddleware) and read
in services or logging without threading request objects through every call.
"""

from __future__ import annotations

from contextvars import ContextVar, Token
from typing import Optional

from .abstraction import IRequestIdContextUtility

_request_id_ctx: ContextVar[Optional[str]] = ContextVar("fast_request_id", default=None)

__all__ = ["IRequestIdContextUtility", "RequestIdContext"]


class RequestIdContext(IRequestIdContextUtility):
    """Access and update the current request id for the running async task."""

    @staticmethod
    def get() -> Optional[str]:
        """Return the current request id, if any."""
        return _request_id_ctx.get()

    @staticmethod
    def set(request_id: Optional[str]) -> Token[Optional[str]]:
        """Bind *request_id* for the current async task.

        Returns:
            A token for use with :meth:`reset`.

        """
        return _request_id_ctx.set(request_id)

    @staticmethod
    def reset(token: Token[Optional[str]]) -> None:
        """Restore the previous value (call in ``finally`` after :meth:`set`)."""
        _request_id_ctx.reset(token)
