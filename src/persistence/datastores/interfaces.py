"""
Datastore protocol interfaces for FastMVC.

Concrete implementations live in this package (Redis, Mongo, Cassandra, …).
``abstractions.datastore`` re-exports these symbols for backward compatibility.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from .abstraction import IDatastores


class IDataStore(IDatastores, ABC):
    """
    Base interface for any data store.

    Provides lifecycle hooks to connect and disconnect underlying clients.
    """

    @abstractmethod
    def connect(self) -> None:
        """Initialize the underlying client/connection."""

    @abstractmethod
    def disconnect(self) -> None:
        """Tear down the underlying client/connection."""


class IRelationalDatabase(IDataStore):
    """
    Interface for relational SQL databases (PostgreSQL, MySQL, SQLite, etc.).

    Implementations should provide a SQLAlchemy `Session` or engine-like
    object via `get_session`.
    """

    @abstractmethod
    def get_session(self) -> Any:  # pragma: no cover - interface only
        """Return a database session/connection object."""

    @abstractmethod
    def ping(self) -> bool:  # pragma: no cover - interface only
        """
        Lightweight health check for the underlying connection.
        """


class IKeyValueStore(IDataStore):
    """
    Interface for key-value stores (e.g., Redis).
    """

    @abstractmethod
    def get(self, key: str) -> Any:  # pragma: no cover - interface only
        """Retrieve a value by key."""

    @abstractmethod
    def set(self, key: str, value: Any, **kwargs: Any) -> None:  # pragma: no cover
        """Set a value by key."""

    @abstractmethod
    def delete(self, key: str) -> None:  # pragma: no cover - interface only
        """Delete a value by key (no-op if the key does not exist)."""

    @abstractmethod
    def exists(self, key: str) -> bool:  # pragma: no cover - interface only
        """Return True if the key exists."""

    @abstractmethod
    def increment(self, key: str, amount: int = 1) -> int:  # pragma: no cover
        """
        Atomically increment an integer value stored at the given key.
        Returns the new value.
        """

    @abstractmethod
    def expire(self, key: str, ttl_seconds: int) -> None:  # pragma: no cover
        """Set a time-to-live in seconds for the given key."""


class IDocumentStore(IDataStore):
    """
    Interface for document databases (e.g., MongoDB, Cosmos DB in document mode).
    """

    @abstractmethod
    def get_database(self) -> Any:  # pragma: no cover - interface only
        """Return a handle to the logical database/namespace."""

    @abstractmethod
    def insert_one(self, collection: str, document: Dict[str, Any]) -> Any:  # pragma: no cover
        """Insert a single document into the given collection."""

    @abstractmethod
    def find_one(
        self, collection: str, filter: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:  # pragma: no cover
        """Find a single document matching the filter."""

    @abstractmethod
    def delete_one(self, collection: str, filter: Dict[str, Any]) -> None:  # pragma: no cover
        """Delete a single document matching the filter."""

    @abstractmethod
    def find_many(
        self, collection: str, filter: Dict[str, Any]
    ) -> list[Dict[str, Any]]:  # pragma: no cover
        """Find all documents matching the filter."""

    @abstractmethod
    def update_one(
        self,
        collection: str,
        filter: Dict[str, Any],
        update: Dict[str, Any],
    ) -> None:  # pragma: no cover
        """Update a single document matching the filter."""

    @abstractmethod
    def update_many(
        self,
        collection: str,
        filter: Dict[str, Any],
        update: Dict[str, Any],
    ) -> None:  # pragma: no cover
        """Update multiple documents matching the filter."""


class IWideColumnStore(IDataStore):
    """
    Interface for wide-column stores (e.g., Cassandra, Scylla).
    """

    @abstractmethod
    def get_session(self) -> Any:  # pragma: no cover - interface only
        """Return a driver/session used to execute CQL-like statements."""

    @abstractmethod
    def execute(self, query: str, parameters: Any | None = None) -> Any:  # pragma: no cover
        """
        Execute a CQL statement and return the driver-specific result object.
        """


class ISearchStore(IDataStore):
    """
    Interface for full-text search engines (e.g., Elasticsearch, OpenSearch).
    """

    @abstractmethod
    def index(
        self,
        index: str,
        id: str,
        document: Dict[str, Any],
    ) -> Any:  # pragma: no cover - interface only
        """Index or update a document by id."""

    @abstractmethod
    def delete(self, index: str, id: str) -> Any:  # pragma: no cover - interface only
        """Delete a document by id."""

    @abstractmethod
    def search(
        self,
        index: str,
        query: Dict[str, Any],
        size: int = 10,
    ) -> Dict[str, Any]:  # pragma: no cover - interface only
        """Execute a search query and return raw hits."""

    @abstractmethod
    def ping(self) -> bool:  # pragma: no cover - interface only
        """Return True if the search cluster is reachable."""
