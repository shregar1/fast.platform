"""Module test_audit.py."""

from __future__ import annotations

"""Tests for ``operations.observability.audit``."""
import operations.observability.audit as audit_module
from operations.observability.audit import AuditEntry, AuditLog, AuditStore, audit_log
from tests.operations.observability.abstraction import IObservabilityTests


class _RecordingStore(AuditStore):
    """Represents the _RecordingStore class."""

    def __init__(self) -> None:
        """Execute __init__ operation."""
        self.entries: list[AuditEntry] = []

    async def store(self, entry: AuditEntry) -> None:
        """Execute store operation.

        Args:
            entry: The entry parameter.

        Returns:
            The result of the operation.
        """
        self.entries.append(entry)


class TestAudit(IObservabilityTests):
    """Represents the TestAudit class."""

    def setup_method(self) -> None:
        """Execute setup_method operation.

        Returns:
            The result of the operation.
        """
        audit_module._audit_log = None

    def teardown_method(self) -> None:
        """Execute teardown_method operation.

        Returns:
            The result of the operation.
        """
        audit_module._audit_log = None

    async def test_log_persists_via_store_and_computes_diff(self) -> None:
        """Execute test_log_persists_via_store_and_computes_diff operation.

        Returns:
            The result of the operation.
        """
        store = _RecordingStore()
        audit = AuditLog(store=store)
        entry = await audit.log(
            action="user.update",
            resource_type="User",
            before_state={"name": "a"},
            after_state={"name": "b"},
            include_diff=True,
        )
        assert len(store.entries) == 1
        assert entry.changes is not None
        assert "name" in entry.changes

    async def test_audit_decorator_async(self) -> None:
        """Execute test_audit_decorator_async operation.

        Returns:
            The result of the operation.
        """
        store = _RecordingStore()
        audit_module.set_audit_log(AuditLog(store=store))

        @audit_log(action="act", resource_type="Res")
        async def do_work() -> int:
            """Execute do_work operation.

            Returns:
                The result of the operation.
            """
            return 7

        assert await do_work() == 7
        assert len(store.entries) == 1
        assert store.entries[0].action == "act"
        assert store.entries[0].success is True
