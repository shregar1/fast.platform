"""
Concrete ``IDataStore`` adapters for Redis, Mongo, Cassandra, Dynamo, Cosmos, Elasticsearch.

Relational DB: ``fast_db``. Object storage: ``fast_storage``.

Prefer ``from fast_datastores import …`` in new code; ``core.datastores`` in pyfastmvc re-exports the same API.
"""

from .cassandra import CassandraWideColumnStore
from .cosmos import CosmosDocumentStore
from .dynamo import DynamoKeyValueStore
from .elasticsearch import ElasticsearchSearchStore
from .mongo import MongoDocumentStore
from .redis_kv import RedisKeyValueStore
from .scylla import ScyllaWideColumnStore

__all__ = [
    "RedisKeyValueStore",
    "MongoDocumentStore",
    "CassandraWideColumnStore",
    "ScyllaWideColumnStore",
    "DynamoKeyValueStore",
    "CosmosDocumentStore",
    "ElasticsearchSearchStore",
]
