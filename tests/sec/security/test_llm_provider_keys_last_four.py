from __future__ import annotations
"""Tests for ``last_four`` (``security.llm_provider_keys``)."""
from tests.sec.security.abstraction import ISecurityTests



from tests.sec.security._llm_provider_keys_load import last_four


class TestLlmProviderKeysLastFour(ISecurityTests):
    def test_last_four(self) -> None:
        assert last_four("sk-abcdef") == "cdef"
        assert last_four("ab") is None
