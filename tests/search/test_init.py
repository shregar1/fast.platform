"""Tests for search."""

import pytest


def test_imports():
    from search import (
        BulkIndexResult,
        FacetedSearchResult,
        ISearchBackend,
        SearchConfiguration,
        SearchConfigurationDTO,
        build_search_backend,
        bulk_index_documents,
        suggest_autocomplete,
        swap_index_alias,
    )
    assert build_search_backend is not None
    assert bulk_index_documents is not None
    assert FacetedSearchResult is not None
    assert BulkIndexResult is not None
    assert suggest_autocomplete is not None
    assert swap_index_alias is not None
