"""Tests for tenant resolution registry and subdomain+header chain."""

from datetime import datetime, timezone

import pytest
from starlette.requests import Request

from tenancy.context import InMemoryTenantStore, Tenant, TenantConfig
from tenancy.resolution import (
    ResolutionStrategy,
    ResolverSpec,
    TenantResolverRegistry,
    subdomain_then_header,
)


def _request(host: str, path: str = "/", extra_headers: dict | None = None) -> Request:
    h = {"host": host}
    if extra_headers:
        h.update(extra_headers)
    hdrs = [(k.lower().encode("latin-1"), str(v).encode("latin-1")) for k, v in h.items()]
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "GET",
        "path": path,
        "raw_path": path.encode("utf-8"),
        "root_path": "",
        "scheme": "http",
        "query_string": b"",
        "headers": hdrs,
        "client": ("127.0.0.1", 12345),
        "server": ("testserver", 80),
    }
    return Request(scope)


@pytest.fixture
async def store_with_acme() -> InMemoryTenantStore:
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


@pytest.mark.asyncio
async def test_registry_build_header(store_with_acme: InMemoryTenantStore) -> None:
    reg = TenantResolverRegistry()
    r = reg.build(store_with_acme, "header", header_name="X-Tenant-ID")
    req = _request("example.com", extra_headers={"X-Tenant-ID": "tid-acme"})
    out = await r.resolve(req)
    assert out is not None and out.slug == "acme"


@pytest.mark.asyncio
async def test_registry_unknown_strategy() -> None:
    reg = TenantResolverRegistry()
    with pytest.raises(KeyError, match="Unknown"):
        reg.build(InMemoryTenantStore(), "not-a-real-strategy")


@pytest.mark.asyncio
async def test_subdomain_then_header_subdomain_wins(store_with_acme: InMemoryTenantStore) -> None:
    resolver = subdomain_then_header(store_with_acme, base_domain="example.com")
    req = _request("acme.example.com", extra_headers={"X-Tenant-ID": "wrong-id"})
    out = await resolver.resolve(req)
    assert out is not None and out.slug == "acme"


@pytest.mark.asyncio
async def test_subdomain_then_header_fallback_header(store_with_acme: InMemoryTenantStore) -> None:
    resolver = subdomain_then_header(store_with_acme, base_domain="example.com")
    req = _request("www.example.com", extra_headers={"X-Tenant-ID": "tid-acme"})
    out = await resolver.resolve(req)
    assert out is not None and out.id == "tid-acme"


@pytest.mark.asyncio
async def test_build_chain_explicit_specs(store_with_acme: InMemoryTenantStore) -> None:
    reg = TenantResolverRegistry()
    chain = reg.build_chain(
        store_with_acme,
        [
            ResolverSpec(ResolutionStrategy.SUBDOMAIN, {"base_domain": "example.com"}),
            ResolverSpec("header", {"header_name": "X-Tenant-ID"}),
        ],
    )
    req = _request("api.example.com", extra_headers={"X-Tenant-ID": "tid-acme"})
    out = await chain.resolve(req)
    assert out is not None and out.id == "tid-acme"


@pytest.mark.asyncio
async def test_list_strategies_includes_defaults() -> None:
    reg = TenantResolverRegistry()
    names = reg.list_strategies()
    assert "header" in names and "subdomain" in names
