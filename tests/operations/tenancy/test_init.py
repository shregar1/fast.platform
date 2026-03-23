from __future__ import annotations

"""Smoke tests for ``tenancy`` package exports."""
from tests.operations.tenancy.abstraction import ITenancyTests


class TestInit(ITenancyTests):
    def test_imports(self) -> None:
        from operations.tenancy import (
            HeaderTenantResolver,
            InMemoryTenantStore,
            ResolutionStrategy,
            Tenant,
            TenantConfig,
            TenantMiddleware,
            TenantResolverRegistry,
            get_current_tenant,
            subdomain_then_header,
        )

        assert Tenant is not None
        assert get_current_tenant is not None
        assert ResolutionStrategy.HEADER.value == "header"
        assert TenantResolverRegistry is not None
        store = InMemoryTenantStore()
        chain = subdomain_then_header(store, base_domain="example.com")
        assert chain is not None
        assert TenantConfig is not None
        assert TenantMiddleware is not None
        assert HeaderTenantResolver is not None
