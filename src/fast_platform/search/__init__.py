"""
FastMVC Search Module

Full-text search integration with Meilisearch, Typesense, and Elasticsearch.
"""

from .index import (
    searchable,
    SearchIndex,
    SearchField,
    SearchResult,
)
from .client import (
    SearchClient,
    MeilisearchClient,
    TypesenseClient,
    ElasticsearchClient,
)
from .query import (
    SearchQuery,
    FilterBuilder,
    SortBuilder,
)

__all__ = [
    "searchable",
    "SearchIndex",
    "SearchField",
    "SearchResult",
    "SearchClient",
    "MeilisearchClient",
    "TypesenseClient",
    "ElasticsearchClient",
    "SearchQuery",
    "FilterBuilder",
    "SortBuilder",
]
