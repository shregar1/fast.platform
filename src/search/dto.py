"""Re-export DTOs for :mod:`search` (canonical definitions live in :mod:`dtos.search`)."""

from __future__ import annotations

from dtos.search import FacetBucket, FacetedSearchResult, SearchHit

__all__ = ["FacetBucket", "FacetedSearchResult", "SearchHit"]
