"""Tests for admin."""
from tests.integrations.admin.abstraction import IAdminTests



class TestInit(IAdminTests):
    def test_imports(self) -> None:
        from admin import (
            AdminUserSummary,
            AuditLogEntry,
            AuditLogHook,
            IAdminUserRepository,
            crud_router_from_model,
            get_admin_router,
        )

        assert AdminUserSummary is not None
        assert AuditLogEntry is not None
        assert IAdminUserRepository is not None
        assert get_admin_router is not None
        assert crud_router_from_model is not None
        assert AuditLogHook is not None
