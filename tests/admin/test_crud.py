"""Tests for generic CRUD router and audit hooks."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict
from sqlalchemy import String, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from sqlalchemy.pool import StaticPool

from fast_admin.abstractions import AuditLogEntry, IAuditLogRepository
from fast_admin.audit_hooks import audit_repository_hook
from fast_admin.crud import crud_router_from_model


class Base(DeclarativeBase):
    pass


class Widget(Base):
    __tablename__ = "widgets"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)


class WidgetCreate(BaseModel):
    name: str


class WidgetUpdate(BaseModel):
    name: Optional[str] = None


class WidgetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


@pytest.fixture
def engine():
    # Single shared in-memory DB across connections (TestClient + Session).
    eng = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(eng)
    return eng


@pytest.fixture
def session_dep(engine):
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    return get_db


def test_crud_roundtrip_and_audit(session_dep):
    events: list[dict[str, Any]] = []

    async def audit_hook(
        *,
        action: str,
        resource_type: str,
        resource_id: Optional[str],
        details: Optional[dict[str, Any]],
        request: Optional[Any] = None,
    ) -> None:
        events.append(
            {
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
            }
        )

    app = FastAPI()
    app.include_router(
        crud_router_from_model(
            Widget,
            create_schema=WidgetCreate,
            update_schema=WidgetUpdate,
            read_schema=WidgetRead,
            session_dep=session_dep,
            resource_type="widgets",
            audit=audit_hook,
        ),
        prefix="/widgets",
    )

    client = TestClient(app)

    assert client.get("/widgets").json() == []

    r = client.post("/widgets", json={"name": "hello"})
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "hello"
    wid = body["id"]

    assert len(events) == 1 and events[0]["action"] == "create"

    r2 = client.get(f"/widgets/{wid}")
    assert r2.status_code == 200 and r2.json()["name"] == "hello"

    r3 = client.patch(f"/widgets/{wid}", json={"name": "bye"})
    assert r3.status_code == 200 and r3.json()["name"] == "bye"
    assert len(events) == 2 and events[1]["action"] == "update"

    r4 = client.delete(f"/widgets/{wid}")
    assert r4.status_code == 204
    assert len(events) == 3 and events[2]["action"] == "delete"

    assert client.get(f"/widgets/{wid}").status_code == 404


def test_audit_repository_hook_and_actor(session_dep):
    class MemAudit(IAuditLogRepository):
        def __init__(self) -> None:
            self.appends: list[dict[str, Any]] = []

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
            self.appends.append(
                {
                    "action": action,
                    "resource_type": resource_type,
                    "actor_id": actor_id,
                    "resource_id": resource_id,
                }
            )
            return AuditLogEntry(
                id="1",
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                details=details or {},
                created_at=datetime.now(timezone.utc),
            )

        async def list_entries(self, **kwargs: Any) -> list[AuditLogEntry]:
            return []

    repo = MemAudit()

    def actor(req: Request) -> Optional[str]:
        return "actor-1"

    app = FastAPI()
    app.include_router(
        crud_router_from_model(
            Widget,
            create_schema=WidgetCreate,
            update_schema=WidgetUpdate,
            read_schema=WidgetRead,
            session_dep=session_dep,
            audit=repo,
            get_actor_id_from_request=actor,
        ),
        prefix="/w",
    )

    client = TestClient(app)
    r = client.post("/w", json={"name": "x"})
    assert r.status_code == 201
    assert len(repo.appends) == 1
    assert repo.appends[0]["actor_id"] == "actor-1"
    assert repo.appends[0]["action"] == "create"


def test_audit_repository_hook_factory(session_dep):
    """Explicit audit_repository_hook without crud get_actor_id wiring."""

    class MemAudit(IAuditLogRepository):
        def __init__(self) -> None:
            self.appends: list[str] = []

        async def append(
            self,
            action: str,
            resource_type: str,
            **kwargs: Any,
        ) -> AuditLogEntry:
            self.appends.append(action)
            return AuditLogEntry(
                id="1",
                action=action,
                resource_type=resource_type,
                created_at=datetime.now(timezone.utc),
            )

        async def list_entries(self, **kwargs: Any) -> list[AuditLogEntry]:
            return []

    repo = MemAudit()
    hook = audit_repository_hook(repo, get_actor_id=lambda r: "u" if r else None)

    app = FastAPI()
    app.include_router(
        crud_router_from_model(
            Widget,
            create_schema=WidgetCreate,
            update_schema=WidgetUpdate,
            read_schema=WidgetRead,
            session_dep=session_dep,
            audit=hook,
        ),
        prefix="/w",
    )

    client = TestClient(app)
    client.post("/w", json={"name": "y"})
    assert repo.appends == ["create"]
