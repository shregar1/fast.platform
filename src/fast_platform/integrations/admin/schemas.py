"""Pydantic DTOs for the admin API (users, roles, audit log)."""

from __future__ import annotations

from datetime import datetime  # noqa: TC003
from typing import Any, Optional

from pydantic import BaseModel

__all__ = [
    "AdminRoleSummary",
    "AdminUserSummary",
    "AuditLogEntry",
]


class AdminUserSummary(BaseModel):
    """Summary of a user for admin listing."""

    id: str
    email: str
    is_active: bool
    created_at: datetime
    roles: list[str] = []


class AdminRoleSummary(BaseModel):
    """Summary of a role for admin listing."""

    id: str
    name: str
    permissions: list[str] = []


class AuditLogEntry(BaseModel):
    """Single audit log entry."""

    id: str
    actor_id: Optional[str] = None
    actor_type: str = "user"
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    details: dict[str, Any] = {}
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    created_at: datetime
