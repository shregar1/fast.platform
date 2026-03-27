"""Repository interfaces for admin users, roles, and audit log."""

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
        """Execute list_users operation.

        Args:
            skip: The skip parameter.
            limit: The limit parameter.
            search: The search parameter.
            active_only: The active_only parameter.

        Returns:
            The result of the operation.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_user(self, user_id: str) -> Optional[AdminUserSummary]:
        """Execute get_user operation.

        Args:
            user_id: The user_id parameter.

        Returns:
            The result of the operation.
        """
        raise NotImplementedError

    @abstractmethod
    async def set_user_active(self, user_id: str, is_active: bool) -> None:
        """Execute set_user_active operation.

        Args:
            user_id: The user_id parameter.
            is_active: The is_active parameter.

        Returns:
            The result of the operation.
        """
        raise NotImplementedError

    @abstractmethod
    async def set_user_roles(self, user_id: str, role_ids: list[str]) -> None:
        """Execute set_user_roles operation.

        Args:
            user_id: The user_id parameter.
            role_ids: The role_ids parameter.

        Returns:
            The result of the operation.
        """
        raise NotImplementedError


class IAdminRoleRepository(IAdmin, ABC):
    """Admin CRUD for roles."""

    @abstractmethod
    async def list_roles(self) -> list[AdminRoleSummary]:
        """Execute list_roles operation.

        Returns:
            The result of the operation.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_role(self, role_id: str) -> Optional[AdminRoleSummary]:
        """Execute get_role operation.

        Args:
            role_id: The role_id parameter.

        Returns:
            The result of the operation.
        """
        raise NotImplementedError

    @abstractmethod
    async def create_role(self, name: str, permissions: list[str]) -> AdminRoleSummary:
        """Execute create_role operation.

        Args:
            name: The name parameter.
            permissions: The permissions parameter.

        Returns:
            The result of the operation.
        """
        raise NotImplementedError

    @abstractmethod
    async def update_role(
        self, role_id: str, name: Optional[str] = None, permissions: Optional[list[str]] = None
    ) -> Optional[AdminRoleSummary]:
        """Execute update_role operation.

        Args:
            role_id: The role_id parameter.
            name: The name parameter.
            permissions: The permissions parameter.

        Returns:
            The result of the operation.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_role(self, role_id: str) -> None:
        """Execute delete_role operation.

        Args:
            role_id: The role_id parameter.

        Returns:
            The result of the operation.
        """
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
        """Execute append operation.

        Args:
            action: The action parameter.
            resource_type: The resource_type parameter.
            actor_id: The actor_id parameter.
            resource_id: The resource_id parameter.
            details: The details parameter.
            ip_address: The ip_address parameter.
            user_agent: The user_agent parameter.

        Returns:
            The result of the operation.
        """
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
        """Execute list_entries operation.

        Args:
            skip: The skip parameter.
            limit: The limit parameter.
            actor_id: The actor_id parameter.
            resource_type: The resource_type parameter.
            resource_id: The resource_id parameter.
            since: The since parameter.

        Returns:
            The result of the operation.
        """
        raise NotImplementedError
