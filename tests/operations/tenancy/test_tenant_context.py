from __future__ import annotations

"""Tests for tenant context and :class:`tenancy.Tenant`."""
import pytest

from tenancy import (
    Tenant,
    TenantConfig,
    TenantContext,
    clear_current_tenant,
    get_current_tenant,
    get_current_tenant_id,
    set_current_tenant,
)
from tests.operations.tenancy.abstraction import ITenancyTests


@pytest.fixture(autouse=True)
def clear_ctx() -> None:
    clear_current_tenant()
    yield
    clear_current_tenant()


class TestTenantContext(ITenancyTests):
    def test_tenant_to_dict_and_features(self) -> None:
        t = Tenant(
            id="t1",
            name="Acme",
            slug="acme",
            config=TenantConfig(features=["billing"], max_users=10),
        )
        d = t.to_dict()
        assert d["id"] == "t1"
        assert d["slug"] == "acme"
        assert t.has_feature("billing")
        assert not t.has_feature("other")

    def test_set_and_get_current_tenant(self) -> None:
        t = Tenant(id="x", name="X", slug="x")
        set_current_tenant(t)
        assert get_current_tenant() is t
        assert get_current_tenant_id() == "x"
        set_current_tenant(None)
        assert get_current_tenant() is None

    def test_tenant_context_manager(self) -> None:
        t = Tenant(id="y", name="Y", slug="y")
        with TenantContext(t):
            assert get_current_tenant_id() == "y"
        assert get_current_tenant() is None
