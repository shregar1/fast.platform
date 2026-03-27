"""Optional audit hooks for CRUD and admin flows.

Use :class:`AuditLogHook` with :func:`crud_router_from_model`, or wrap
:class:`~fast_admin.repositories.IAuditLogRepository` with
:func:`audit_repository_hook`.
"""

from __future__ import annotations

from typing import Any, Callable, Optional, Protocol, Union, cast

from .abstractions import IAuditLogRepository


class AuditLogHook(Protocol):
    """Async callback invoked after a successful create, update, or delete."""

    async def __call__(
        self,
        *,
        action: str,
        resource_type: str,
        resource_id: Optional[str],
        details: Optional[dict[str, Any]],
        request: Optional[Any] = None,
    ) -> None: ...


AuditTarget = Union[AuditLogHook, IAuditLogRepository, None]


def audit_repository_hook(
    repo: IAuditLogRepository,
    *,
    get_actor_id: Optional[Callable[[Any], Optional[str]]] = None,
    get_ip_address: Optional[Callable[[Any], Optional[str]]] = None,
    get_user_agent: Optional[Callable[[Any], Optional[str]]] = None,
) -> AuditLogHook:
    """Wrap an :class:`~fast_admin.repositories.IAuditLogRepository` as an
    :class:`AuditLogHook`, mapping ``request`` through optional extractors.
    """

    async def hook(
        *,
        action: str,
        resource_type: str,
        resource_id: Optional[str],
        details: Optional[dict[str, Any]],
        request: Optional[Any] = None,
    ) -> None:
        actor_id = get_actor_id(request) if get_actor_id and request else None
        ip = get_ip_address(request) if get_ip_address and request else None
        ua = get_user_agent(request) if get_user_agent and request else None
        await repo.append(
            action,
            resource_type,
            actor_id=actor_id,
            resource_id=resource_id,
            details=details,
            ip_address=ip,
            user_agent=ua,
        )

    return hook


def as_audit_hook(
    target: AuditTarget,
    *,
    get_actor_id: Optional[Callable[[Any], Optional[str]]] = None,
    get_ip_address: Optional[Callable[[Any], Optional[str]]] = None,
    get_user_agent: Optional[Callable[[Any], Optional[str]]] = None,
) -> Optional[AuditLogHook]:
    """Normalize ``None``, a plain :class:`AuditLogHook`, or an
    :class:`~fast_admin.repositories.IAuditLogRepository` into a single hook
    (or ``None``).
    """
    if target is None:
        return None
    if isinstance(target, IAuditLogRepository):
        return audit_repository_hook(
            cast("IAuditLogRepository", target),
            get_actor_id=get_actor_id,
            get_ip_address=get_ip_address,
            get_user_agent=get_user_agent,
        )
    return cast("AuditLogHook", target)


__all__ = [
    "AuditLogHook",
    "AuditTarget",
    "audit_repository_hook",
    "as_audit_hook",
]
