"""Tests for fast_tenancy."""

import pytest


def test_imports():
    from fast_tenancy import (
        Tenant,
        TenantConfig,
        get_current_tenant,
        TenantMiddleware,
        HeaderTenantResolver,
        InMemoryTenantStore,
        TenantResolverRegistry,
        ResolutionStrategy,
        subdomain_then_header,
    )
    assert Tenant is not None
    assert get_current_tenant is not None
    assert ResolutionStrategy.HEADER.value == "header"
    assert TenantResolverRegistry is not None
    store = InMemoryTenantStore()
    chain = subdomain_then_header(store, base_domain="example.com")
    assert chain is not None
