"""Tests for collection name helpers."""

import pytest

from data.vectors.names import VectorCollectionNamesUtility

from tests.data_platform.vectors.abstraction import IVectorTests


class TestNames(IVectorTests):
    """Represents the TestNames class."""

    def test_sanitize_collection_segment_basic(self):
        """Execute test_sanitize_collection_segment_basic operation.

        Returns:
            The result of the operation.
        """
        U = VectorCollectionNamesUtility
        assert U.sanitize_collection_segment("Acme Corp") == "acme-corp"
        assert U.sanitize_collection_segment("  tenant__42  ") == "tenant-42"
        assert U.sanitize_collection_segment("") == "default"
        assert U.sanitize_collection_segment("   ", fallback="x") == "x"

    def test_prefixed_collection_name_basic(self):
        """Execute test_prefixed_collection_name_basic operation.

        Returns:
            The result of the operation.
        """
        U = VectorCollectionNamesUtility
        assert U.prefixed_collection_name("acme-corp", "kb-articles") == "acme-corp__kb-articles"
        assert U.prefixed_collection_name("tenant_42", "docs", separator="_") == "tenant_42_docs"

    def test_prefixed_collection_name_empty_separator(self):
        """Execute test_prefixed_collection_name_empty_separator operation.

        Returns:
            The result of the operation.
        """
        with pytest.raises(ValueError, match="separator"):
            VectorCollectionNamesUtility.prefixed_collection_name("a", "b", separator="")

    def test_prefixed_collection_name_truncation_preserves_prefix(self):
        """Execute test_prefixed_collection_name_truncation_preserves_prefix operation.

        Returns:
            The result of the operation.
        """
        long_base = "x" * 300
        out = VectorCollectionNamesUtility.prefixed_collection_name("ns", long_base, max_length=40)
        assert len(out) == 40
        assert out.startswith("ns__")

    def test_prefixed_collection_name_truncation_prefix_only_when_huge_namespace(self):
        """Execute test_prefixed_collection_name_truncation_prefix_only_when_huge_namespace operation.

        Returns:
            The result of the operation.
        """
        huge = "y" * 500
        out = VectorCollectionNamesUtility.prefixed_collection_name(huge, "base", max_length=20)
        assert len(out) == 20
