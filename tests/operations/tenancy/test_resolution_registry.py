"""Module test_resolution_registry.py."""

from __future__ import annotations

"""Tests for :class:`operations.tenancy.resolution.TenantResolverRegistry`."""
import pytest

from fast_platform.operations.tenancy.context import InMemoryTenantStore
from fast_platform.operations.tenancy.resolution import TenantResolverRegistry
from tests.operations.tenancy.abstraction import ITenancyTests
from tests.operations.tenancy.helpers import make_request


class TestResolutionRegistry(ITenancyTests):
    """Represents the TestResolutionRegistry class."""

    @pytest.mark.asyncio
    async def test_registry_build_header(self, store_with_acme: InMemoryTenantStore) -> None:
        """Execute test_registry_build_header operation.

        Args:
            store_with_acme: The store_with_acme parameter.

        Returns:
            The result of the operation.
        """
        reg = TenantResolverRegistry()
        r = reg.build(store_with_acme, "header", header_name="X-Tenant-ID")
        req = make_request("example.com", extra_headers={"X-Tenant-ID": "tid-acme"})
        out = await r.resolve(req)
        assert out is not None and out.slug == "acme"

    @pytest.mark.asyncio
    async def test_registry_unknown_strategy(self) -> None:
        """Execute test_registry_unknown_strategy operation.

        Returns:
            The result of the operation.
        """
        reg = TenantResolverRegistry()
        with pytest.raises(KeyError, match="Unknown"):
            reg.build(InMemoryTenantStore(), "not-a-real-strategy")

    @pytest.mark.asyncio
    async def test_list_strategies_includes_defaults(self) -> None:
        """Execute test_list_strategies_includes_defaults operation.

        Returns:
            The result of the operation.
        """
        reg = TenantResolverRegistry()
        names = reg.list_strategies()
        assert "header" in names and "subdomain" in names
