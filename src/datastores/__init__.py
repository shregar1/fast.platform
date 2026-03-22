"""
Concrete ``IDataStore`` adapters for Redis, Mongo, Cassandra, Dynamo, Cosmos, Elasticsearch.

Relational DB: ``fast_db``. Object storage: ``fast_storage``.

Prefer ``from fast_datastores import …`` in new code; ``core.datastores`` in pyfastmvc re-exports the same API.
"""

from fast_datastores.cassandra import CassandraWideColumnStore
from fast_datastores.cosmos import CosmosDocumentStore
from fast_datastores.dynamo import DynamoKeyValueStore
from fast_datastores.elasticsearch import ElasticsearchSearchStore
from fast_datastores.mongo import MongoDocumentStore
from fast_datastores.redis_kv import RedisKeyValueStore
from fast_datastores.scylla import ScyllaWideColumnStore

__all__ = [
    "RedisKeyValueStore",
    "MongoDocumentStore",
    "CassandraWideColumnStore",
    "ScyllaWideColumnStore",
    "DynamoKeyValueStore",
    "CosmosDocumentStore",
    "ElasticsearchSearchStore",
]
