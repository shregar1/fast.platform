"""Tests for collection name helpers."""

import pytest

from tests.data_platform.vectors.abstraction import IVectorTests
from vectors.names import prefixed_collection_name, sanitize_collection_segment


class TestNames(IVectorTests):
    def test_sanitize_collection_segment_basic(self):
        assert sanitize_collection_segment("Acme Corp") == "acme-corp"
        assert sanitize_collection_segment("  tenant__42  ") == "tenant-42"
        assert sanitize_collection_segment("") == "default"
        assert sanitize_collection_segment("   ", fallback="x") == "x"

    def test_prefixed_collection_name_basic(self):
        assert prefixed_collection_name("acme-corp", "kb-articles") == "acme-corp__kb-articles"
        assert prefixed_collection_name("tenant_42", "docs", separator="_") == "tenant_42_docs"

    def test_prefixed_collection_name_empty_separator(self):
        with pytest.raises(ValueError, match="separator"):
            prefixed_collection_name("a", "b", separator="")

    def test_prefixed_collection_name_truncation_preserves_prefix(self):
        long_base = "x" * 300
        out = prefixed_collection_name("ns", long_base, max_length=40)
        assert len(out) == 40
        assert out.startswith("ns__")

    def test_prefixed_collection_name_truncation_prefix_only_when_huge_namespace(self):
        huge = "y" * 500
        out = prefixed_collection_name(huge, "base", max_length=20)
        assert len(out) == 20
