"""
Repository interfaces for admin users, roles, and audit log.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Optional

from .abstraction import IAdmin

if TYPE_CHECKING:
    from datetime import datetime

    from .schemas import AdminRoleSummary, AdminUserSummary, AuditLogEntry

__all__ = [
    "IAdminRoleRepository",
    "IAdminUserRepository",
    "IAuditLogRepository",
]


class IAdminUserRepository(IAdmin, ABC):
    """Admin view over users (list, toggle active, assign roles)."""

    @abstractmethod
    async def list_users(
        self,
        *,
        skip: int = 0,
        limit: int = 50,
        search: Optional[str] = None,
        active_only: Optional[bool] = None,
    ) -> list[AdminUserSummary]:
        raise NotImplementedError

    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[AdminUserSummary]:
        raise NotImplementedError

    @abstractmethod
    async def set_user_active(self, user_id: str, is_active: bool) -> None:
        raise NotImplementedError

    @abstractmethod
    async def set_user_roles(self, user_id: str, role_ids: list[str]) -> None:
        raise NotImplementedError


class IAdminRoleRepository(IAdmin, ABC):
    """Admin CRUD for roles."""

    @abstractmethod
    async def list_roles(self) -> list[AdminRoleSummary]:
        raise NotImplementedError

    @abstractmethod
    async def get_role(self, role_id: str) -> Optional[AdminRoleSummary]:
        raise NotImplementedError

    @abstractmethod
    async def create_role(self, name: str, permissions: list[str]) -> AdminRoleSummary:
        raise NotImplementedError

    @abstractmethod
    async def update_role(
        self, role_id: str, name: Optional[str] = None, permissions: Optional[list[str]] = None
    ) -> Optional[AdminRoleSummary]:
        raise NotImplementedError

    @abstractmethod
    async def delete_role(self, role_id: str) -> None:
        raise NotImplementedError


class IAuditLogRepository(IAdmin, ABC):
    """Append-only audit log for admin review."""

    @abstractmethod
    async def append(
        self,
        action: str,
        resource_type: str,
        *,
        actor_id: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLogEntry:
        raise NotImplementedError

    @abstractmethod
    async def list_entries(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        actor_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        since: Optional[datetime] = None,
    ) -> list[AuditLogEntry]:
        raise NotImplementedError
