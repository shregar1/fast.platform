"""Optional FastAPI router for admin API.

Mount under /admin and protect with your auth (e.g. require admin role).
"""

from typing import Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel

from .repositories import IAdminRoleRepository, IAdminUserRepository, IAuditLogRepository
from .schemas import AdminRoleSummary, AdminUserSummary, AuditLogEntry


def get_admin_router(
    user_repo: Optional[IAdminUserRepository] = None,
    role_repo: Optional[IAdminRoleRepository] = None,
    audit_repo: Optional[IAuditLogRepository] = None,
    prefix: str = "/admin",
) -> APIRouter:
    """Build an admin API router. Pass repos for the sections you want to expose."""
    router = APIRouter(prefix=prefix, tags=["admin"])

    if user_repo is not None:

        @router.get("/users", response_model=list[AdminUserSummary])
        async def list_users(
            skip: int = Query(0, ge=0),
            limit: int = Query(50, ge=1, le=100),
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
            return await user_repo.list_users(
                skip=skip, limit=limit, search=search, active_only=active_only
            )

        @router.get("/users/{user_id}", response_model=AdminUserSummary)
        async def get_user(user_id: str) -> AdminUserSummary:
            """Execute get_user operation.

            Args:
                user_id: The user_id parameter.

            Returns:
                The result of the operation.
            """
            u = await user_repo.get_user(user_id)
            if u is None:
                from fastapi import HTTPException

                raise HTTPException(404, "User not found")
            return u

        class ActiveBody(BaseModel):
            """Represents the ActiveBody class."""

            is_active: bool

        @router.patch("/users/{user_id}/active")
        async def set_user_active(user_id: str, body: ActiveBody) -> dict[str, bool]:
            """Execute set_user_active operation.

            Args:
                user_id: The user_id parameter.
                body: The body parameter.

            Returns:
                The result of the operation.
            """
            await user_repo.set_user_active(user_id, body.is_active)
            return {"ok": True}

        class RolesBody(BaseModel):
            """Represents the RolesBody class."""

            role_ids: list[str] = []

        @router.put("/users/{user_id}/roles")
        async def set_user_roles(user_id: str, body: RolesBody) -> dict[str, bool]:
            """Execute set_user_roles operation.

            Args:
                user_id: The user_id parameter.
                body: The body parameter.

            Returns:
                The result of the operation.
            """
            await user_repo.set_user_roles(user_id, body.role_ids)
            return {"ok": True}

    if role_repo is not None:

        @router.get("/roles", response_model=list[AdminRoleSummary])
        async def list_roles() -> list[AdminRoleSummary]:
            """Execute list_roles operation.

            Returns:
                The result of the operation.
            """
            return await role_repo.list_roles()

        @router.get("/roles/{role_id}", response_model=AdminRoleSummary)
        async def get_role(role_id: str) -> AdminRoleSummary:
            """Execute get_role operation.

            Args:
                role_id: The role_id parameter.

            Returns:
                The result of the operation.
            """
            r = await role_repo.get_role(role_id)
            if r is None:
                from fastapi import HTTPException

                raise HTTPException(404, "Role not found")
            return r

    if audit_repo is not None:

        @router.get("/audit", response_model=list[AuditLogEntry])
        async def list_audit(
            skip: int = Query(0, ge=0),
            limit: int = Query(100, ge=1, le=500),
            actor_id: Optional[str] = None,
            resource_type: Optional[str] = None,
            resource_id: Optional[str] = None,
        ) -> list[AuditLogEntry]:
            """Execute list_audit operation.

            Args:
                skip: The skip parameter.
                limit: The limit parameter.
                actor_id: The actor_id parameter.
                resource_type: The resource_type parameter.
                resource_id: The resource_id parameter.

            Returns:
                The result of the operation.
            """
            return await audit_repo.list_entries(
                skip=skip,
                limit=limit,
                actor_id=actor_id,
                resource_type=resource_type,
                resource_id=resource_id,
            )

    return router
