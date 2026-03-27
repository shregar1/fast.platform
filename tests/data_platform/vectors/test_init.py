"""Tests for vectors."""

from tests.data_platform.vectors.abstraction import IVectorTests


class TestInit(IVectorTests):
    """Represents the TestInit class."""

    def test_imports(self):
        """Execute test_imports operation.

        Returns:
            The result of the operation.
        """
        from data.vectors import VectorCollectionNamesUtility, build_vector_store

        assert build_vector_store is not None
        assert VectorCollectionNamesUtility.prefixed_collection_name("a", "b") == "a__b"
        assert VectorCollectionNamesUtility.sanitize_collection_segment("X") == "x"
