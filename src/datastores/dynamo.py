"""
AWS DynamoDB key-value / document store implementation.

Provides a very thin wrapper around `boto3.resource("dynamodb")` that
implements the `IKeyValueStore` interface for single-table style access.
"""

from time import time
from typing import Any, Dict, Optional

from loguru import logger

from .interfaces import IKeyValueStore

try:  # Optional dependency
    import boto3  # type: ignore
except Exception:  # pragma: no cover - optional import
    boto3 = None  # type: ignore[assignment]


class DynamoKeyValueStore(IKeyValueStore):
    """
    DynamoDB-backed key-value/document store.

    This implementation is intentionally minimal and focused on single-table
    access with a primary key named `pk`. Projects are expected to subclass
    this or wrap it in higher-level repositories for richer models.
    """

    def __init__(
        self,
        table_name: str,
        region_name: str = "us-east-1",
        endpoint_url: Optional[str] = None,
    ) -> None:
        self._table_name = table_name
        self._region_name = region_name
        self._endpoint_url = endpoint_url
        self._resource: Any = None
        self._table: Any = None

    def connect(self) -> None:
        if boto3 is None:  # pragma: no cover - guarded by optional import
            raise RuntimeError(
                "boto3 is not installed. Install it with `pip install boto3`."
            )
        self._resource = boto3.resource(
            "dynamodb",
            region_name=self._region_name,
            endpoint_url=self._endpoint_url,
        )
        self._table = self._resource.Table(self._table_name)
        logger.info(
            "Connected DynamoKeyValueStore",
            table=self._table_name,
            region=self._region_name,
        )

    def disconnect(self) -> None:
        # boto3 resources use HTTP connection pooling and do not require
        # explicit shutdown; we just drop references.
        self._table = None
        self._resource = None
        logger.info("Disconnected DynamoKeyValueStore")

    def get(self, key: str) -> Any:
        if self._table is None:
            raise RuntimeError("DynamoKeyValueStore is not connected.")
        response = self._table.get_item(Key={"pk": key})
        return response.get("Item")

    def set(self, key: str, value: Any, **kwargs: Any) -> None:
        if self._table is None:
            raise RuntimeError("DynamoKeyValueStore is not connected.")
        item: Dict[str, Any] = {"pk": key}
        if isinstance(value, dict):
            item.update(value)
        else:
            item["value"] = value
        self._table.put_item(Item=item, **kwargs)

    def delete(self, key: str) -> None:
        if self._table is None:
            raise RuntimeError("DynamoKeyValueStore is not connected.")
        self._table.delete_item(Key={"pk": key})

    def exists(self, key: str) -> bool:
        return self.get(key) is not None

    def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment a numeric `value` attribute on the stored item.
        Creates the item if it does not exist.
        """
        if self._table is None:
            raise RuntimeError("DynamoKeyValueStore is not connected.")
        response = self._table.update_item(
            Key={"pk": key},
            UpdateExpression="ADD #v :inc",
            ExpressionAttributeNames={"#v": "value"},
            ExpressionAttributeValues={":inc": amount},
            ReturnValues="UPDATED_NEW",
        )
        return int(response["Attributes"]["value"])

    def expire(self, key: str, ttl_seconds: int) -> None:
        """
        Set a TTL attribute on the item (if a TTL attribute is configured on the table).
        This is a best-effort helper; projects may override to use a specific TTL field name.
        """
        if self._table is None:
            raise RuntimeError("DynamoKeyValueStore is not connected.")
        # Default TTL attribute name commonly used in DynamoDB examples.
        # Callers are free to override this class if they use a different name.
        expires_at = int(time()) + ttl_seconds
        self._table.update_item(
            Key={"pk": key},
            UpdateExpression="SET #ttl = :ttl",
            ExpressionAttributeNames={"#ttl": "ttl"},
            ExpressionAttributeValues={":ttl": expires_at},
        )


