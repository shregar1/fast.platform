"""Starlette/FastAPI middleware for sampled request analytics."""

from __future__ import annotations

import random
from typing import Any, Callable, cast

from .base import IAnalyticsBackend

try:
    from starlette.middleware.base import BaseHTTPMiddleware as _BaseHTTPMiddleware
    from starlette.requests import Request
    from starlette.responses import Response

    _STARLETTE = True
except ImportError:  # pragma: no cover - optional web extra
    _STARLETTE = False

    class _BaseHTTPMiddleware:  # type: ignore[no-redef]
        def __init__(self, app: Any) -> None:
            self.app = app

    class Request:  # type: ignore[no-redef]
        ...

    class Response:  # type: ignore[no-redef]
        ...


def default_analytics_user_key(request: Request) -> str:
    """Resolve distinct id from ``x-user-id``, ``request.state.user_id``, or ``anonymous``."""
    h = request.headers.get("x-user-id")
    if h:
        return h
    uid = getattr(request.state, "user_id", None)
    if uid is not None:
        return str(uid)
    return "anonymous"


BaseHTTPMiddleware = cast(Any, _BaseHTTPMiddleware)


class AnalyticsSamplingMiddleware(BaseHTTPMiddleware):
    """
    After each response, with probability ``sample_rate``, track ``http.request`` with path, method, status.
    """

    def __init__(
        self,
        app: Any,
        backend: IAnalyticsBackend,
        *,
        sample_rate: float = 0.01,
        user_key: Callable[[Request], str] = default_analytics_user_key,
        max_events_per_user_per_minute: int = 0,
    ):
        if not _STARLETTE:  # pragma: no cover
            raise RuntimeError("starlette required: pip install fast_analytics[web]")
        super().__init__(app)
        if max_events_per_user_per_minute > 0:
            from .rate_limit import RateLimitedAnalyticsBackend

            backend = RateLimitedAnalyticsBackend(
                backend,
                max_events_per_user_per_minute=max_events_per_user_per_minute,
            )
        self._backend = backend
        self._sample_rate = min(1.0, max(0.0, sample_rate))
        self._user_key = user_key

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        if self._sample_rate <= 0:
            return response
        if random.random() >= self._sample_rate:
            return response
        distinct_id = self._user_key(request)
        self._backend.track(
            distinct_id,
            "http.request",
            {
                "path": request.url.path,
                "method": request.method,
                "status_code": response.status_code,
            },
        )
        return response
