"""Module test_logging.py."""

from __future__ import annotations

"""Tests for ``operations.observability.logging``."""
import json
from types import SimpleNamespace

from operations.observability.logging import (
    StructuredLogger,
    clear_log_context,
    get_log_context,
    json_formatter,
    set_log_context,
)
from tests.operations.observability.abstraction import IObservabilityTests


class TestLoggingModule(IObservabilityTests):
    """Represents the TestLoggingModule class."""

    def teardown_method(self) -> None:
        """Execute teardown_method operation.

        Returns:
            The result of the operation.
        """
        clear_log_context()

    def test_set_get_clear_context(self) -> None:
        """Execute test_set_get_clear_context operation.

        Returns:
            The result of the operation.
        """
        set_log_context(
            request_id="req-1", user_id="u-2", tenant_id="t-3", trace_id="tr-4", extra="x"
        )
        ctx = get_log_context()
        assert ctx["request_id"] == "req-1"
        assert ctx["user_id"] == "u-2"
        assert ctx["tenant_id"] == "t-3"
        assert ctx["trace_id"] == "tr-4"
        assert ctx["extra"] == "x"
        clear_log_context()
        assert get_log_context() == {}

    def test_json_formatter_merges_context(self) -> None:
        """Execute test_json_formatter_merges_context operation.

        Returns:
            The result of the operation.
        """
        set_log_context(request_id="rid-9")
        record = {
            "level": SimpleNamespace(name="INFO"),
            "message": "hello",
            "name": "n",
            "module": "mod",
            "function": "fn",
            "line": 42,
            "extra": {"custom": 1},
        }
        line = json_formatter(record)
        parsed = json.loads(line.strip())
        assert parsed["message"] == "hello"
        assert parsed["request_id"] == "rid-9"
        assert parsed["custom"] == 1

    def test_structured_logger_levels_do_not_raise(self) -> None:
        """Execute test_structured_logger_levels_do_not_raise operation.

        Returns:
            The result of the operation.
        """
        sl = StructuredLogger("test_svc", json_output=False)
        sl.debug("d")
        sl.info("i")
        sl.warning("w")
        sl.error("e")
