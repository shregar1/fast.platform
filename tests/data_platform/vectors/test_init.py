"""Tests for vectors."""
from tests.data_platform.vectors.abstraction import IVectorTests

import pytest

class TestInit(IVectorTests):

    def test_imports(self):
        from vectors import IVectorStore, VectorsConfiguration, VectorsConfigurationDTO, build_vector_store, prefixed_collection_name, sanitize_collection_segment
        assert build_vector_store is not None
        assert prefixed_collection_name('a', 'b') == 'a__b'
        assert sanitize_collection_segment('X') == 'x'
