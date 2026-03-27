"""fast_admin – CRUD API for admin resources (users, roles, audit log) for FastMVC."""

from .audit_hooks import (
    AuditLogHook,
    AuditTarget,
    as_audit_hook,
    audit_repository_hook,
)
from .crud import crud_router_from_model
from .repositories import IAdminRoleRepository, IAdminUserRepository, IAuditLogRepository
from .router import get_admin_router
from .schemas import AdminRoleSummary, AdminUserSummary, AuditLogEntry

__version__ = "0.1.1"

__all__ = [
    "AdminUserSummary",
    "AdminRoleSummary",
    "AuditLogEntry",
    "IAdminUserRepository",
    "IAdminRoleRepository",
    "IAuditLogRepository",
    "get_admin_router",
    "crud_router_from_model",
    "AuditLogHook",
    "AuditTarget",
    "audit_repository_hook",
    "as_audit_hook",
]
