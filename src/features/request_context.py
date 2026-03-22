"""
Build feature-flag evaluation context from a Starlette/FastAPI request.
"""

from __future__ import annotations

from typing import Any, Optional


def feature_flags_context_from_request(
    request: Any,
    *,
    user_id_header: str = "x-user-id",
    tenant_id_header: str = "x-tenant-id",
) -> dict[str, Any]:
    """
    Build ``{"key", "user_key", ...}`` from ``request.state``, headers, and query params.

    ``request`` may be a Starlette/FastAPI ``Request`` or any object with ``.headers``,
    ``.query_params``, and optional ``.state``.
    """
    ctx: dict[str, Any] = {}

    state = getattr(request, "state", None)
    if state is not None:
        uid = getattr(state, "user_id", None) or getattr(state, "user_key", None)
        tid = getattr(state, "tenant_id", None)
        if uid is not None:
            ctx["key"] = str(uid)
            ctx["user_key"] = str(uid)
        if tid is not None:
            ctx["tenant_id"] = str(tid)

    headers = getattr(request, "headers", {}) or {}
    low = {k.lower(): v for k, v in dict(headers).items()}
    if "key" not in ctx:
        h = low.get(user_id_header.lower())
        if h:
            ctx["key"] = str(h)
            ctx["user_key"] = str(h)
    if "tenant_id" not in ctx:
        h = low.get(tenant_id_header.lower())
        if h:
            ctx["tenant_id"] = str(h)

    qp = getattr(request, "query_params", None)
    if qp is not None:
        if "key" not in ctx and qp.get("user_id"):
            ctx["key"] = str(qp["user_id"])
            ctx["user_key"] = str(qp["user_id"])
        if "tenant_id" not in ctx and qp.get("tenant_id"):
            ctx["tenant_id"] = str(qp["tenant_id"])

    if "key" not in ctx:
        ctx["key"] = "anonymous"
        ctx["user_key"] = "anonymous"

    return ctx
