"""Generic FastAPI CRUD router from a SQLAlchemy 2.0 model and Pydantic v2 schemas.

Requires SQLAlchemy (included with ``fast-platform``; install ``sqlalchemy`` if using a minimal env).

Note: ``from __future__ import annotations`` is omitted so FastAPI can resolve
dynamic ``create_schema`` / ``update_schema`` / ``read_schema`` types on routes.
"""

from typing import Any, Callable, Optional, Type

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel

from .audit_hooks import AuditLogHook, AuditTarget, as_audit_hook


def crud_router_from_model(
    model: Any,
    *,
    create_schema: Type[BaseModel],
    update_schema: Type[BaseModel],
    read_schema: Type[BaseModel],
    session_dep: Callable[..., Any],
    resource_type: Optional[str] = None,
    prefix: str = "",
    tags: Optional[list[str]] = None,
    audit: AuditTarget = None,
    get_actor_id_from_request: Optional[Callable[[Request], Optional[str]]] = None,
    get_ip_from_request: Optional[Callable[[Request], Optional[str]]] = None,
    get_user_agent_from_request: Optional[Callable[[Request], Optional[str]]] = None,
) -> APIRouter:
    """Build an ``APIRouter`` with list/create/read/update/delete for a single table.

    **Requirements**

    - Model must use a **single-column** primary key.
    - ``read_schema`` should use ``model_config = ConfigDict(from_attributes=True)``
      so ORM instances serialize correctly.
    - ``create_schema`` / ``update_schema`` field names should match mapped
      attribute names on the model (excluding the primary key on create if
      auto-generated).

    **Audit**

    Pass ``audit`` as an :class:`~fast_admin.audit_hooks.AuditLogHook` or
    :class:`~fast_admin.repositories.IAuditLogRepository`. Hooks run **after**
    a successful create, update, or delete. Use ``get_*_from_request`` when
    ``audit`` is a repository to populate actor / IP / user-agent.

    **Session**

    ``session_dep`` is used as ``Depends(session_dep)`` and must yield or return
    a SQLAlchemy :class:`~sqlalchemy.orm.Session`.
    """
    try:
        from sqlalchemy import inspect as sa_inspect
        from sqlalchemy import select
    except ImportError as e:  # pragma: no cover - exercised when sqlalchemy missing
        raise RuntimeError(
            "crud_router_from_model requires SQLAlchemy. Install: pip install sqlalchemy"
        ) from e

    mapper = sa_inspect(model).mapper
    if len(mapper.primary_key) != 1:
        raise ValueError("crud_router_from_model requires exactly one primary key column")

    pk_col = mapper.primary_key[0]
    pk_name = pk_col.key
    pk_python = getattr(pk_col.type, "python_type", None)

    rtype = resource_type or getattr(model, "__tablename__", model.__name__).lower()

    def _parse_id(raw: str) -> Any:
        """Execute _parse_id operation.

        Args:
            raw: The raw parameter.

        Returns:
            The result of the operation.
        """
        if pk_python is int:
            try:
                return int(raw)
            except ValueError as err:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid id"
                ) from err
        return raw

    hook: Optional[AuditLogHook] = as_audit_hook(
        audit,
        get_actor_id=get_actor_id_from_request,
        get_ip_address=get_ip_from_request,
        get_user_agent=get_user_agent_from_request,
    )

    async def _audit(
        *,
        action: str,
        resource_id: Optional[str],
        details: Optional[dict[str, Any]],
        request: Optional[Request],
    ) -> None:
        """Execute _audit operation.

        Args:
            action: The action parameter.
            resource_id: The resource_id parameter.
            details: The details parameter.
            request: The request parameter.

        Returns:
            The result of the operation.
        """
        if hook is None:
            return
        await hook(
            action=action,
            resource_type=rtype,
            resource_id=resource_id,
            details=details,
            request=request,
        )

    tag_list = tags if tags is not None else [rtype]
    router = APIRouter(prefix=prefix, tags=tag_list)

    @router.get("", response_model=list[read_schema])
    async def list_items(
        skip: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=500),
        db: Any = Depends(session_dep),
    ) -> list[BaseModel]:
        """Execute list_items operation.

        Args:
            skip: The skip parameter.
            limit: The limit parameter.
            db: The db parameter.

        Returns:
            The result of the operation.
        """
        rows = db.scalars(select(model).offset(skip).limit(limit)).all()
        return [read_schema.model_validate(r) for r in rows]

    @router.post("", response_model=read_schema, status_code=status.HTTP_201_CREATED)
    async def create_item(
        body: create_schema,
        request: Request,
        db: Any = Depends(session_dep),
    ) -> BaseModel:
        """Execute create_item operation.

        Args:
            body: The body parameter.
            request: The request parameter.
            db: The db parameter.

        Returns:
            The result of the operation.
        """
        data = body.model_dump(exclude_unset=True)
        if pk_name in data:
            del data[pk_name]
        obj = model(**data)
        db.add(obj)
        db.commit()
        db.refresh(obj)
        pk_val = getattr(obj, pk_name)
        await _audit(
            action="create",
            resource_id=str(pk_val),
            details={"payload": body.model_dump()},
            request=request,
        )
        return read_schema.model_validate(obj)

    @router.get("/{item_id}", response_model=read_schema)
    async def get_item(
        item_id: str,
        db: Any = Depends(session_dep),
    ) -> BaseModel:
        """Execute get_item operation.

        Args:
            item_id: The item_id parameter.
            db: The db parameter.

        Returns:
            The result of the operation.
        """
        pk = _parse_id(item_id)
        obj = db.get(model, pk)
        if obj is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        return read_schema.model_validate(obj)

    @router.patch("/{item_id}", response_model=read_schema)
    async def update_item(
        item_id: str,
        body: update_schema,
        request: Request,
        db: Any = Depends(session_dep),
    ) -> BaseModel:
        """Execute update_item operation.

        Args:
            item_id: The item_id parameter.
            body: The body parameter.
            request: The request parameter.
            db: The db parameter.

        Returns:
            The result of the operation.
        """
        pk = _parse_id(item_id)
        obj = db.get(model, pk)
        if obj is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        patch = body.model_dump(exclude_unset=True)
        before = {k: getattr(obj, k, None) for k in patch}
        for k, v in patch.items():
            setattr(obj, k, v)
        db.commit()
        db.refresh(obj)
        await _audit(
            action="update",
            resource_id=str(pk),
            details={"before": before, "after": patch},
            request=request,
        )
        return read_schema.model_validate(obj)

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_item(
        item_id: str,
        request: Request,
        db: Any = Depends(session_dep),
    ) -> None:
        """Execute delete_item operation.

        Args:
            item_id: The item_id parameter.
            request: The request parameter.
            db: The db parameter.

        Returns:
            The result of the operation.
        """
        pk = _parse_id(item_id)
        obj = db.get(model, pk)
        if obj is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
        snapshot = read_schema.model_validate(obj).model_dump()
        db.delete(obj)
        db.commit()
        await _audit(
            action="delete",
            resource_id=str(pk),
            details={"snapshot": snapshot},
            request=request,
        )
        return None

    return router


__all__ = ["crud_router_from_model"]
