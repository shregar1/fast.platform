"""Tests for vectors."""

from tests.data_platform.vectors.abstraction import IVectorTests


class TestInit(IVectorTests):
    def test_imports(self):
        from data.vectors import VectorCollectionNamesUtility, build_vector_store

        assert build_vector_store is not None
        assert VectorCollectionNamesUtility.prefixed_collection_name("a", "b") == "a__b"
        assert VectorCollectionNamesUtility.sanitize_collection_segment("X") == "x"
