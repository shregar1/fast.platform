"""Module test_cache_lease_redact.py."""

from __future__ import annotations

"""Tests for TTL cache, leased auto-refresh, and redaction helpers."""
import time
from fast_platform.sec.secrets.cache import CachedSecretsBackend
from fast_platform.sec.secrets.lease import LeasedSecretsBackend
from fast_platform.sec.secrets.redact import redact_json_for_log, redact_mapping, redact_text
from typing import Any, Dict, Optional
from unittest.mock import MagicMock

import pytest

from tests.sec.secrets.abstraction import ISecretsTests


class TestCacheLeaseRedact(ISecretsTests):
    """Represents the TestCacheLeaseRedact class."""

    class MemBackend:
        """Represents the MemBackend class."""

        name = "mem"

        def __init__(self) -> None:
            """Execute __init__ operation."""
            self.store: Dict[str, str] = {}

        def get_secret(self, key: str, **kwargs: Any) -> Optional[str]:
            """Execute get_secret operation.

            Args:
                key: The key parameter.

            Returns:
                The result of the operation.
            """
            return self.store.get(key)

        def set_secret(self, key: str, value: str) -> None:
            """Execute set_secret operation.

            Args:
                key: The key parameter.
                value: The value parameter.

            Returns:
                The result of the operation.
            """
            self.store[key] = value

    def test_cached_ttl_and_force_refresh(self) -> None:
        """Execute test_cached_ttl_and_force_refresh operation.

        Returns:
            The result of the operation.
        """
        inner = MagicMock()
        inner.get_secret = MagicMock(side_effect=["a", "b"])
        inner.set_secret = MagicMock()
        inner.name = "x"
        c = CachedSecretsBackend(inner, ttl_seconds=60, name="c")
        assert c.get_secret("k") == "a"
        assert c.get_secret("k") == "a"
        assert inner.get_secret.call_count == 1
        assert c.get_secret("k", force_refresh=True) == "b"
        assert inner.get_secret.call_count == 2

    def test_rotation_callback(self) -> None:
        """Execute test_rotation_callback operation.

        Returns:
            The result of the operation.
        """
        seen: list[tuple[str, Optional[str], str]] = []

        def on_rot(key: str, old: Optional[str], new: str) -> None:
            """Execute on_rot operation.

            Args:
                key: The key parameter.
                old: The old parameter.
                new: The new parameter.

            Returns:
                The result of the operation.
            """
            seen.append((key, old, new))

        inner = MagicMock()
        inner.get_secret = MagicMock(side_effect=["v1", "v2"])
        inner.set_secret = MagicMock()
        inner.name = "x"
        c = CachedSecretsBackend(
            inner, ttl_seconds=1, on_rotation=on_rot, notify_on_first_fetch=True
        )
        assert c.get_secret("k") == "v1"
        assert seen == [("k", None, "v1")]
        assert c.get_secret("k", force_refresh=True) == "v2"
        assert seen[-1] == ("k", "v1", "v2")

    def test_lease_triggers_background_refresh(self) -> None:
        """Execute test_lease_triggers_background_refresh operation.

        Returns:
            The result of the operation.
        """
        b = self.MemBackend()
        b.store["k"] = "first"
        lease = LeasedSecretsBackend(b, ttl_seconds=1, refresh_at_ratio=0.05, name="l")
        assert lease.get_secret("k") == "first"
        b.store["k"] = "second"
        time.sleep(0.3)
        assert lease.get_secret("k") == "second"
        lease.stop()

    def test_lease_stop_cancels(self) -> None:
        """Execute test_lease_stop_cancels operation.

        Returns:
            The result of the operation.
        """
        inner = MagicMock()
        inner.get_secret = MagicMock(return_value="x")
        inner.set_secret = MagicMock()
        inner.name = "i"
        lease = LeasedSecretsBackend(inner, ttl_seconds=10, refresh_at_ratio=0.99, name="l")
        lease.get_secret("k")
        lease.stop()
        time.sleep(0.05)

    def test_lease_invalid_ratio(self) -> None:
        """Execute test_lease_invalid_ratio operation.

        Returns:
            The result of the operation.
        """
        inner = MagicMock()
        inner.name = "i"
        with pytest.raises(ValueError):
            LeasedSecretsBackend(inner, ttl_seconds=10, refresh_at_ratio=1.0)

    def test_redact_text_order(self) -> None:
        """Execute test_redact_text_order operation.

        Returns:
            The result of the operation.
        """
        assert (
            redact_text("hello supersecret and sub", "sub", "supersecret", mask="[REDACTED]")
            == "hello [REDACTED] and [REDACTED]"
        )

    def test_redact_mapping(self) -> None:
        """Execute test_redact_mapping operation.

        Returns:
            The result of the operation.
        """
        data = {"password": "s3cr3t", "ok": 1, "nested": {"token": "abc"}}
        out = redact_mapping(data, {"password", "token"})
        assert out["password"] == "***"
        assert out["ok"] == 1
        assert out["nested"]["token"] == "***"

    def test_redact_json_for_log(self) -> None:
        """Execute test_redact_json_for_log operation.

        Returns:
            The result of the operation.
        """
        s = redact_json_for_log({"x": "secret"}, "secret", mask="?")
        assert "?" in s
        assert '"x"' in s
