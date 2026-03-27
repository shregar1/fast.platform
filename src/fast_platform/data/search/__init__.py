"""fast_search – Search backends (Meilisearch, Typesense, OpenSearch) for FastMVC."""

from fast_platform import SearchConfiguration, SearchConfigurationDTO

from .base import ISearchBackend, build_search_backend
from .bulk import BulkIndexError, BulkIndexResult, bulk_index_documents
from ...core.dtos.search import FacetBucket, FacetedSearchResult, SearchHit
from .rollover import swap_index_alias
from .suggest import suggest_autocomplete

__version__ = "0.3.0"

__all__ = [
    "BulkIndexError",
    "BulkIndexResult",
    "FacetBucket",
    "FacetedSearchResult",
    "ISearchBackend",
    "SearchConfiguration",
    "SearchConfigurationDTO",
    "SearchHit",
    "build_search_backend",
    "bulk_index_documents",
    "suggest_autocomplete",
    "swap_index_alias",
]
