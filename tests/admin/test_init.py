"""Tests for fast_admin."""

import pytest


def test_imports():
    from fast_admin import (
        AdminUserSummary,
        AuditLogEntry,
        IAdminUserRepository,
        get_admin_router,
        crud_router_from_model,
        AuditLogHook,
    )
    assert get_admin_router is not None
    assert crud_router_from_model is not None
    assert AuditLogHook is not None
