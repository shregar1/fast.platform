"""Module test_resolution_chain.py."""

from __future__ import annotations

"""Tests for ``subdomain_then_header`` and explicit resolver chains."""
import pytest

from fast_platform.operations.tenancy.context import InMemoryTenantStore
from fast_platform.operations.tenancy.resolution import (
    ResolutionStrategy,
    ResolverSpec,
    TenantResolverRegistry,
    subdomain_then_header,
)
from tests.operations.tenancy.abstraction import ITenancyTests
from tests.operations.tenancy.helpers import make_request


class TestResolutionChain(ITenancyTests):
    """Represents the TestResolutionChain class."""

    @pytest.mark.asyncio
    async def test_subdomain_then_header_subdomain_wins(
        self, store_with_acme: InMemoryTenantStore
    ) -> None:
        """Execute test_subdomain_then_header_subdomain_wins operation.

        Args:
            store_with_acme: The store_with_acme parameter.

        Returns:
            The result of the operation.
        """
        resolver = subdomain_then_header(store_with_acme, base_domain="example.com")
        req = make_request("acme.example.com", extra_headers={"X-Tenant-ID": "wrong-id"})
        out = await resolver.resolve(req)
        assert out is not None and out.slug == "acme"

    @pytest.mark.asyncio
    async def test_subdomain_then_header_fallback_header(
        self, store_with_acme: InMemoryTenantStore
    ) -> None:
        """Execute test_subdomain_then_header_fallback_header operation.

        Args:
            store_with_acme: The store_with_acme parameter.

        Returns:
            The result of the operation.
        """
        resolver = subdomain_then_header(store_with_acme, base_domain="example.com")
        req = make_request("www.example.com", extra_headers={"X-Tenant-ID": "tid-acme"})
        out = await resolver.resolve(req)
        assert out is not None and out.id == "tid-acme"

    @pytest.mark.asyncio
    async def test_build_chain_explicit_specs(self, store_with_acme: InMemoryTenantStore) -> None:
        """Execute test_build_chain_explicit_specs operation.

        Args:
            store_with_acme: The store_with_acme parameter.

        Returns:
            The result of the operation.
        """
        reg = TenantResolverRegistry()
        chain = reg.build_chain(
            store_with_acme,
            [
                ResolverSpec(ResolutionStrategy.SUBDOMAIN, {"base_domain": "example.com"}),
                ResolverSpec("header", {"header_name": "X-Tenant-ID"}),
            ],
        )
        req = make_request("api.example.com", extra_headers={"X-Tenant-ID": "tid-acme"})
        out = await chain.resolve(req)
        assert out is not None and out.id == "tid-acme"
