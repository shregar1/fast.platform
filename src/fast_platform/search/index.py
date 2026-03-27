"""Search index definitions."""

from typing import Dict, Any, List, Optional, Type, Callable
from dataclasses import dataclass
from functools import wraps
import json


@dataclass
class SearchField:
    """Definition of a searchable field."""

    name: str
    type: str = "string"  # string, int, float, bool, date
    searchable: bool = True
    filterable: bool = False
    sortable: bool = False
    facet: bool = False

    def to_schema(self) -> Dict[str, Any]:
        """Execute to_schema operation.

        Returns:
            The result of the operation.
        """
        return {
            "name": self.name,
            "type": self.type,
            "searchable": self.searchable,
            "filterable": self.filterable,
            "sortable": self.sortable,
            "facet": self.facet,
        }


@dataclass
class SearchResult:
    """Search result item."""

    id: str
    document: Dict[str, Any]
    score: float
    highlights: Optional[Dict[str, List[str]]] = None


class SearchIndex:
    """Search index manager."""

    def __init__(self, name: str, client: Optional[Any] = None, primary_key: str = "id"):
        """Execute __init__ operation.

        Args:
            name: The name parameter.
            client: The client parameter.
            primary_key: The primary_key parameter.
        """
        self.name = name
        self.client = client
        self.primary_key = primary_key
        self._fields: List[SearchField] = []

    def add_field(self, field: SearchField) -> "SearchIndex":
        """Add a field to the index."""
        self._fields.append(field)
        return self

    async def create(self) -> None:
        """Create the index."""
        if self.client:
            await self.client.create_index(self.name, {"primaryKey": self.primary_key})

    async def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents to the index."""
        if self.client:
            await self.client.add_documents(self.name, documents)

    async def update_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Update documents in the index."""
        if self.client:
            await self.client.update_documents(self.name, documents)

    async def delete_document(self, document_id: str) -> None:
        """Delete a document."""
        if self.client:
            await self.client.delete_document(self.name, document_id)

    async def search(
        self, query: str, options: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search the index."""
        if not self.client:
            return []

        results = await self.client.search(self.name, query, options or {})

        return [
            SearchResult(
                id=r["id"],
                document=r.get("document", r),
                score=r.get("score", 0.0),
                highlights=r.get("highlights"),
            )
            for r in results.get("hits", [])
        ]

    async def delete(self) -> None:
        """Delete the index."""
        if self.client:
            await self.client.delete_index(self.name)


def searchable(
    index: str,
    fields: Optional[List[SearchField]] = None,
    auto_index: bool = True,
    primary_key: str = "id",
):
    """Decorator to make a model searchable.

    Args:
        index: Index name
        fields: List of searchable fields
        auto_index: Whether to auto-index on save
        primary_key: Primary key field

    """

    def decorator(cls):
        """Execute decorator operation.

        Returns:
            The result of the operation.
        """
        cls._search_index = index
        cls._search_fields = fields or []
        cls._search_auto_index = auto_index
        cls._search_primary_key = primary_key
        cls._is_searchable = True

        # Add methods to class
        original_init = cls.__init__

        @wraps(original_init)
        def new_init(self, *args, **kwargs):
            """Execute new_init operation.

            Returns:
                The result of the operation.
            """
            original_init(self, *args, **kwargs)
            self._search_dirty = True

        cls.__init__ = new_init

        # Method to get search document
        def to_search_document(self) -> Dict[str, Any]:
            """Convert to search document."""
            doc = {}
            for field in self._search_fields:
                value = getattr(self, field.name, None)
                if value is not None:
                    doc[field.name] = value
            doc[primary_key] = getattr(self, primary_key)
            return doc

        cls.to_search_document = to_search_document

        return cls

    return decorator
