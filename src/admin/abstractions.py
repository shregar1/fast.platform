"""
Admin resource abstractions: users, roles, audit log.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


# ----- Schemas (optional DTOs for admin API) -----


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


# ----- Repository interfaces -----


class IAdminUserRepository(ABC):
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


class IAdminRoleRepository(ABC):
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
    async def update_role(self, role_id: str, name: Optional[str] = None, permissions: Optional[list[str]] = None) -> Optional[AdminRoleSummary]:
        raise NotImplementedError

    @abstractmethod
    async def delete_role(self, role_id: str) -> None:
        raise NotImplementedError


class IAuditLogRepository(ABC):
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
