"""
Optional FastAPI router for admin API.

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
    """
    Build an admin API router. Pass repos for the sections you want to expose.
    """
    router = APIRouter(prefix=prefix, tags=["admin"])

    if user_repo is not None:

        @router.get("/users", response_model=list[AdminUserSummary])
        async def list_users(
            skip: int = Query(0, ge=0),
            limit: int = Query(50, ge=1, le=100),
            search: Optional[str] = None,
            active_only: Optional[bool] = None,
        ) -> list[AdminUserSummary]:
            return await user_repo.list_users(
                skip=skip, limit=limit, search=search, active_only=active_only
            )

        @router.get("/users/{user_id}", response_model=AdminUserSummary)
        async def get_user(user_id: str) -> AdminUserSummary:
            u = await user_repo.get_user(user_id)
            if u is None:
                from fastapi import HTTPException

                raise HTTPException(404, "User not found")
            return u

        class ActiveBody(BaseModel):
            is_active: bool

        @router.patch("/users/{user_id}/active")
        async def set_user_active(user_id: str, body: ActiveBody) -> dict[str, bool]:
            await user_repo.set_user_active(user_id, body.is_active)
            return {"ok": True}

        class RolesBody(BaseModel):
            role_ids: list[str] = []

        @router.put("/users/{user_id}/roles")
        async def set_user_roles(user_id: str, body: RolesBody) -> dict[str, bool]:
            await user_repo.set_user_roles(user_id, body.role_ids)
            return {"ok": True}

    if role_repo is not None:

        @router.get("/roles", response_model=list[AdminRoleSummary])
        async def list_roles() -> list[AdminRoleSummary]:
            return await role_repo.list_roles()

        @router.get("/roles/{role_id}", response_model=AdminRoleSummary)
        async def get_role(role_id: str) -> AdminRoleSummary:
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
            return await audit_repo.list_entries(
                skip=skip,
                limit=limit,
                actor_id=actor_id,
                resource_type=resource_type,
                resource_id=resource_id,
            )

    return router
