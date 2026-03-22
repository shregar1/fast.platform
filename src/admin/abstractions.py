"""
Admin resource abstractions: users, roles, audit log.

Prefer importing from :mod:`admin.schemas` and :mod:`admin.repositories`;
this module re-exports the same names for backward compatibility.
"""

from __future__ import annotations

from .repositories import (
    IAdminRoleRepository,
    IAdminUserRepository,
    IAuditLogRepository,
)
from .schemas import AdminRoleSummary, AdminUserSummary, AuditLogEntry

__all__ = [
    "AdminRoleSummary",
    "AdminUserSummary",
    "AuditLogEntry",
    "IAdminUserRepository",
    "IAdminRoleRepository",
    "IAuditLogRepository",
]
