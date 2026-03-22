"""Search configuration DTO and structured search result types (facets)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from pydantic import Field

from .abstraction import IDTO
from .meilisearch import MeilisearchDTO


class SearchConfigurationDTO(IDTO):
    default_backend: str = "meilisearch"
    meilisearch: MeilisearchDTO = Field(default_factory=MeilisearchDTO)


@dataclass(slots=True)
class SearchHit:
    """One search hit."""

    document: dict[str, Any]
    id: Optional[str] = None
    score: Optional[float] = None
    #: Matched fragments per field (often HTML), when the backend returns highlights.
    highlights: Optional[Dict[str, List[str]]] = None


@dataclass(slots=True)
class FacetBucket:
    """Single facet value with document count."""

    value: str
    count: int


@dataclass(slots=True)
class FacetedSearchResult:
    """
    Search hits plus facet distributions (when the backend supports them).

    ``facets`` maps a field name to ordered facet buckets (value + count).
    """

    hits: List[SearchHit]
    facets: Dict[str, List[FacetBucket]] = field(default_factory=dict)
    total: int = 0
