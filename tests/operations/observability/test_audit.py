from __future__ import annotations

"""Tests for ``observability.audit``."""
import observability.audit as audit_module
from observability.audit import AuditEntry, AuditLog, AuditStore, audit_log
from tests.operations.observability.abstraction import IObservabilityTests


class _RecordingStore(AuditStore):
    def __init__(self) -> None:
        self.entries: list[AuditEntry] = []

    async def store(self, entry: AuditEntry) -> None:
        self.entries.append(entry)


class TestAudit(IObservabilityTests):
    def setup_method(self) -> None:
        audit_module._audit_log = None

    def teardown_method(self) -> None:
        audit_module._audit_log = None

    async def test_log_persists_via_store_and_computes_diff(self) -> None:
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
        store = _RecordingStore()
        audit_module.set_audit_log(AuditLog(store=store))

        @audit_log(action="act", resource_type="Res")
        async def do_work() -> int:
            return 7

        assert await do_work() == 7
        assert len(store.entries) == 1
        assert store.entries[0].action == "act"
        assert store.entries[0].success is True
