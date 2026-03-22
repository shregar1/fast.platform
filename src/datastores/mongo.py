"""
MongoDB document store implementation.

Provides a minimal wrapper around `pymongo.MongoClient` implementing the
`IDocumentStore` interface.

The actual connection parameters are passed in at construction time so
projects can decide whether to read them from environment variables,
JSON config, or other sources.
"""

from typing import Any, Dict, Optional

from loguru import logger

from fast_datastores.interfaces import IDocumentStore

try:  # Optional dependency
    from pymongo import MongoClient  # type: ignore
except Exception:  # pragma: no cover - optional import
    MongoClient = None  # type: ignore[misc, assignment]


class MongoDocumentStore(IDocumentStore):
    """
    MongoDB-backed document store.
    """

    def __init__(self, uri: str, database: str) -> None:
        self._uri = uri
        self._database_name = database
        self._client: Optional[Any] = None

    def connect(self) -> None:
        if MongoClient is None:  # pragma: no cover - guarded by optional import
            raise RuntimeError(
                "pymongo is not installed. Install it with `pip install pymongo`."
            )
        self._client = MongoClient(self._uri)
        logger.info("Connected MongoDocumentStore", uri=self._uri, database=self._database_name)

    def disconnect(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
            logger.info("Disconnected MongoDocumentStore")

    def get_database(self) -> Any:
        if self._client is None:
            raise RuntimeError("MongoDocumentStore is not connected.")
        return self._client[self._database_name]

    def insert_one(self, collection: str, document: Dict[str, Any]) -> Any:
        db = self.get_database()
        return db[collection].insert_one(document)

    def find_one(self, collection: str, filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        db = self.get_database()
        result = db[collection].find_one(filter)
        # pymongo returns a dict-like object; we return it as-is.
        return result

    def delete_one(self, collection: str, filter: Dict[str, Any]) -> None:
        db = self.get_database()
        db[collection].delete_one(filter)

    def find_many(self, collection: str, filter: Dict[str, Any]) -> list[Dict[str, Any]]:
        db = self.get_database()
        cursor = db[collection].find(filter)
        return list(cursor)

    def update_one(
        self,
        collection: str,
        filter: Dict[str, Any],
        update: Dict[str, Any],
    ) -> None:
        db = self.get_database()
        db[collection].update_one(filter, update)

    def update_many(
        self,
        collection: str,
        filter: Dict[str, Any],
        update: Dict[str, Any],
    ) -> None:
        db = self.get_database()
        db[collection].update_many(filter, update)


