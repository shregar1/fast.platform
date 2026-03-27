"""Azure Cosmos DB document store implementation.

Provides a minimal wrapper around the `azure-cosmos` client implementing
the `IDocumentStore` interface.
"""

from typing import Any, Dict, Optional

from loguru import logger

from .interfaces import IDocumentStore

try:  # Optional dependency
    from azure.cosmos import CosmosClient  # type: ignore
except Exception:  # pragma: no cover - optional import
    CosmosClient = None  # type: ignore[misc, assignment]


class CosmosDocumentStore(IDocumentStore):
    """Cosmos DB-backed document store."""

    def __init__(self, account_uri: str, account_key: str, database: str) -> None:
        """Execute __init__ operation.

        Args:
            account_uri: The account_uri parameter.
            account_key: The account_key parameter.
            database: The database parameter.
        """
        self._account_uri = account_uri
        self._account_key = account_key
        self._database_name = database
        self._client: Any = None
        self._database: Any = None

    def connect(self) -> None:
        """Execute connect operation.

        Returns:
            The result of the operation.
        """
        if CosmosClient is None:  # pragma: no cover - guarded by optional import
            raise RuntimeError(
                "azure-cosmos is not installed. Install it with `pip install azure-cosmos`."
            )
        self._client = CosmosClient(self._account_uri, credential=self._account_key)
        self._database = self._client.create_database_if_not_exists(id=self._database_name)
        logger.info(
            "Connected CosmosDocumentStore",
            account_uri=self._account_uri,
            database=self._database_name,
        )

    def disconnect(self) -> None:
        """Execute disconnect operation.

        Returns:
            The result of the operation.
        """
        # azure-cosmos uses HTTP under the hood; closing the client is enough.
        self._client = None
        self._database = None
        logger.info("Disconnected CosmosDocumentStore")

    def get_database(self) -> Any:
        """Execute get_database operation.

        Returns:
            The result of the operation.
        """
        if self._database is None:
            raise RuntimeError("CosmosDocumentStore is not connected.")
        return self._database

    def insert_one(self, collection: str, document: Dict[str, Any]) -> Any:
        """Insert a document into the given container (collection)."""
        database = self.get_database()
        container = database.create_container_if_not_exists(id=collection, partition_key="/pk")  # type: ignore[arg-type]
        return container.create_item(body=document)

    def find_one(self, collection: str, filter: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document using a simple equality-based filter.

        For more complex queries, callers should use the low-level Cosmos client.
        """
        database = self.get_database()
        container = database.create_container_if_not_exists(id=collection, partition_key="/pk")  # type: ignore[arg-type]
        # Build a basic query like: SELECT * FROM c WHERE c.field = @value
        if not filter:
            query = "SELECT * FROM c"
            params: list[Dict[str, Any]] = []
        else:
            (field, value), *_rest = filter.items()
            query = f"SELECT * FROM c WHERE c.{field} = @value"
            params = [{"name": "@value", "value": value}]
        items = list(
            container.query_items(
                query=query,
                parameters=params,
                enable_cross_partition_query=True,
            )
        )
        if not items:
            return None
        return items[0]

    def delete_one(self, collection: str, filter: Dict[str, Any]) -> None:
        """Delete a single document matching the filter.

        The filter must contain at least the `id` and partition key (`pk` by default)
        for this helper to work reliably.
        """
        database = self.get_database()
        container = database.create_container_if_not_exists(id=collection, partition_key="/pk")  # type: ignore[arg-type]
        item = self.find_one(collection, filter)
        if not item:
            return
        item_id = item.get("id")
        pk = item.get("pk")
        if item_id is None or pk is None:
            return
        container.delete_item(item=item_id, partition_key=pk)

    def find_many(self, collection: str, filter: Dict[str, Any]) -> list[Dict[str, Any]]:
        """Find all documents matching the filter.

        This is implemented as a simple equality query on the first key in the filter.
        For more complex scenarios, use the low-level Cosmos SDK directly.
        """
        database = self.get_database()
        container = database.create_container_if_not_exists(id=collection, partition_key="/pk")  # type: ignore[arg-type]
        if not filter:
            query = "SELECT * FROM c"
            params: list[Dict[str, Any]] = []
        else:
            (field, value), *_rest = filter.items()
            query = f"SELECT * FROM c WHERE c.{field} = @value"
            params = [{"name": "@value", "value": value}]
        items = list(
            container.query_items(
                query=query,
                parameters=params,
                enable_cross_partition_query=True,
            )
        )
        return items

    def update_one(
        self,
        collection: str,
        filter: Dict[str, Any],
        update: Dict[str, Any],
    ) -> None:
        """Apply a partial update to a single document.

        For simplicity, this implementation loads the document and applies the
        update dict as a shallow merge before replacing the item.
        """
        database = self.get_database()
        container = database.create_container_if_not_exists(id=collection, partition_key="/pk")  # type: ignore[arg-type]
        item = self.find_one(collection, filter)
        if not item:
            return
        item.update(update)
        container.replace_item(item=item, body=item)

    def update_many(
        self,
        collection: str,
        filter: Dict[str, Any],
        update: Dict[str, Any],
    ) -> None:
        """Apply the same shallow update to all documents matching the filter."""
        database = self.get_database()
        container = database.create_container_if_not_exists(id=collection, partition_key="/pk")  # type: ignore[arg-type]
        items = self.find_many(collection, filter)
        for item in items:
            item.update(update)
            container.replace_item(item=item, body=item)
