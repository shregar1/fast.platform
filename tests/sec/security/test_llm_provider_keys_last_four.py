"""Module test_llm_provider_keys_last_four.py."""

from __future__ import annotations

"""Tests for ``last_four`` (``sec.security.llm_provider_keys``)."""
from tests.sec.security._llm_provider_keys_load import last_four
from tests.sec.security.abstraction import ISecurityTests


class TestLlmProviderKeysLastFour(ISecurityTests):
    """Represents the TestLlmProviderKeysLastFour class."""

    def test_last_four(self) -> None:
        """Execute test_last_four operation.

        Returns:
            The result of the operation.
        """
        assert last_four("sk-abcdef") == "cdef"
        assert last_four("ab") is None
