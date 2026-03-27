"""Fixtures for ``tests/tenancy``."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from fast_platform.operations.tenancy.context import InMemoryTenantStore, Tenant, TenantConfig


@pytest.fixture
async def store_with_acme() -> InMemoryTenantStore:
    """Execute store_with_acme operation.

    Returns:
        The result of the operation.
    """
    store = InMemoryTenantStore()
    t = Tenant(
        id="tid-acme",
        name="Acme",
        slug="acme",
        is_active=True,
        created_at=datetime.now(timezone.utc),
        config=TenantConfig(),
    )
    await store.create(t)
    return store
