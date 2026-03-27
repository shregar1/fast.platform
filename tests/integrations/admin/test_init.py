"""Tests for admin."""

from tests.integrations.admin.abstraction import IAdminTests


class TestInit(IAdminTests):
    """Represents the TestInit class."""

    def test_imports(self) -> None:
        """Execute test_imports operation.

        Returns:
            The result of the operation.
        """
        from fast_platform.integrations.admin import (
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
