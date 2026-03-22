from tests.data_platform.vectors.abstraction import IVectorTests
import builtins
import sys
import types
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple
import pytest

class TestBackends(IVectorTests):

    def test_is_vector_store_abstract_methods_raise_not_implemented(self):
        from vectors.base import IVectorStore

        class DummyStore(IVectorStore):
            name = 'dummy'

            def upsert(self, index_name: str, vectors: List[Tuple[str, List[float], Optional[dict[str, Any]]]]) -> None:
                return super().upsert(index_name=index_name, vectors=vectors)

            def query(self, index_name: str, vector: List[float], *, top_k: int=10, filter: Optional[dict[str, Any]]=None):
                return super().query(index_name=index_name, vector=vector, top_k=top_k, filter=filter)

            def delete_index(self, index_name: str) -> None:
                return super().delete_index(index_name=index_name)
        s = DummyStore()
        with pytest.raises(NotImplementedError):
            s.upsert('i', [('id', [0.1], None)])
        with pytest.raises(NotImplementedError):
            s.query('i', [0.1])
        with pytest.raises(NotImplementedError):
            s.delete_index('i')

    def test_build_vector_store_selection_and_import_error(self, monkeypatch):
        from vectors import base as vector_base

        class FakeCfg:

            def __init__(self):
                self.pinecone = types.SimpleNamespace(enabled=True, api_key='pc', environment=None, index_name='main-index')
                self.qdrant = types.SimpleNamespace(enabled=True, url='http://qdrant', api_key=None)
                self.weaviate = types.SimpleNamespace(enabled=True, url='http://weaviate', api_key=None)
        monkeypatch.setattr(vector_base, 'VectorsConfiguration', lambda: types.SimpleNamespace(get_config=lambda: FakeCfg()), raising=True)
        fake_pinecone = types.ModuleType('pinecone')
        fake_pinecone.Pinecone = lambda api_key: types.SimpleNamespace(Index=lambda index_name: types.SimpleNamespace(upsert=lambda vectors: None, query=lambda **kw: types.SimpleNamespace(matches=[])), delete_index=lambda index_name: None)
        sys.modules['pinecone'] = fake_pinecone
        fake_qdrant = types.ModuleType('qdrant_client')
        fake_models = types.ModuleType('qdrant_client.models')

        @dataclass
        class PointStruct:
            id: str
            vector: List[float]
            payload: dict

        @dataclass
        class FieldCondition:
            key: str
            match: Any

        @dataclass
        class MatchValue:
            value: Any

        @dataclass
        class Filter:
            must: list

        class FakeHit:

            def __init__(self, id: str):
                self.id = id
                self.score = 1.0
                self.payload = {'k': 'v'}

        class FakeQdrantClient:

            def __init__(self, url: str, api_key: Optional[str]=None):
                self.url = url
                self.api_key = api_key
                self.upsert_calls: list[dict[str, Any]] = []

            def upsert(self, *, collection_name: str, points: list):
                self.upsert_calls.append({'collection_name': collection_name, 'points': points})

            def search(self, *, collection_name: str, query_vector: list, limit: int, query_filter: Any=None):
                self.last_search = {'collection_name': collection_name, 'query_vector': query_vector, 'limit': limit, 'query_filter': query_filter}
                return [FakeHit('id1')]

            def delete_collection(self, collection_name: str):
                self.deleted = collection_name
        fake_qdrant.QdrantClient = FakeQdrantClient
        fake_models.PointStruct = PointStruct
        fake_models.FieldCondition = FieldCondition
        fake_models.MatchValue = MatchValue
        fake_models.Filter = Filter
        fake_qdrant.models = fake_models
        sys.modules['qdrant_client'] = fake_qdrant
        sys.modules['qdrant_client.models'] = fake_models
        fake_weaviate = types.ModuleType('weaviate')

        class FakeObj:

            def __init__(self):
                self.uuid = 'uuid-1'
                self.metadata = types.SimpleNamespace(distance=None)
                self.properties = {'p': 1}

        class FakeQueryResult:

            def __init__(self):
                self.objects = [FakeObj()]

        class FakeCollectionQuery:

            def near_vector(self, *, near_vector: list, limit: int):
                return FakeQueryResult()

        class FakeBatch:

            def __init__(self):
                self.added: list[dict[str, Any]] = []

            def add_object(self, *, properties: dict, vector: list):
                self.added.append({'properties': properties, 'vector': vector})

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

        class FakeBatchMgr:

            def dynamic(self):
                return FakeBatch()

        class FakeCollection:

            def __init__(self):
                self.query = FakeCollectionQuery()
                self.batch = FakeBatchMgr()

        class FakeCollections:

            def __init__(self):
                self._cols: dict[str, FakeCollection] = {}
                self.deleted: list[str] = []

            def get(self, name: str) -> FakeCollection:
                if name not in self._cols:
                    self._cols[name] = FakeCollection()
                return self._cols[name]

            def delete(self, name: str):
                self.deleted.append(name)

        class FakeWeaviateClient:

            def __init__(self):
                self.collections = FakeCollections()
        fake_weaviate.connect_to_local = lambda host, port, grpc_port: FakeWeaviateClient()
        fake_weaviate.connect_to_weaviate_cloud = lambda cluster_url, auth_credentials: FakeWeaviateClient()
        fake_weaviate.auth = types.SimpleNamespace(AuthApiKey=lambda api_key: api_key)
        sys.modules['weaviate'] = fake_weaviate
        assert vector_base.build_vector_store('qdrant') is not None
        assert vector_base.build_vector_store('weaviate') is not None
        assert vector_base.build_vector_store('pinecone') is not None
        real_import = builtins.__import__

        def _fail_backend_import(name, *args, **kwargs):
            if 'qdrant_backend' in name or 'weaviate_backend' in name or 'pinecone_backend' in name:
                raise ImportError(name)
            return real_import(name, *args, **kwargs)
        monkeypatch.setattr(builtins, '__import__', _fail_backend_import)
        sys.modules.pop('vectors.qdrant_backend', None)
        sys.modules.pop('vectors.weaviate_backend', None)
        sys.modules.pop('vectors.pinecone_backend', None)
        assert vector_base.build_vector_store('qdrant') is None
        assert vector_base.build_vector_store('weaviate') is None
        assert vector_base.build_vector_store('pinecone') is None

    def test_qdrant_backend_upsert_query_and_delete_with_filter(self, monkeypatch):
        from vectors.qdrant_backend import QdrantVectorStore
        if 'qdrant_client' not in sys.modules:
            fake_qdrant = types.ModuleType('qdrant_client')
            fake_models = types.ModuleType('qdrant_client.models')

            @dataclass
            class PointStruct:
                id: str
                vector: List[float]
                payload: dict

            @dataclass
            class FieldCondition:
                key: str
                match: Any

            @dataclass
            class MatchValue:
                value: Any

            @dataclass
            class Filter:
                must: list

            class FakeHit:

                def __init__(self, id: str):
                    self.id = id
                    self.score = 1.0
                    self.payload = {'k': 'v'}

            class FakeQdrantClient:

                def __init__(self, url: str, api_key: Optional[str]=None):
                    self.url = url
                    self.api_key = api_key

                def upsert(self, *, collection_name: str, points: list):
                    self.last_upsert = {'collection_name': collection_name, 'points': points}

                def search(self, *, collection_name: str, query_vector: list, limit: int, query_filter: Any=None):
                    return [FakeHit('id1')]

                def delete_collection(self, collection_name: str):
                    self.deleted = collection_name
            fake_qdrant.QdrantClient = FakeQdrantClient
            fake_models.PointStruct = PointStruct
            fake_models.FieldCondition = FieldCondition
            fake_models.MatchValue = MatchValue
            fake_models.Filter = Filter
            fake_qdrant.models = fake_models
            sys.modules['qdrant_client'] = fake_qdrant
            sys.modules['qdrant_client.models'] = fake_models
        store = QdrantVectorStore(url='http://qdrant', api_key=None)
        store.upsert('idx', [('id1', [0.1, 0.2], {'a': 1})])
        hits = store.query('idx', [0.1, 0.2], top_k=5, filter={'k': 'v'})
        assert hits[0][0] == 'id1'
        store.delete_index('idx')

    def test_weaviate_backend_upsert_query_and_delete(self, monkeypatch):
        from vectors.weaviate_backend import WeaviateVectorStore
        if 'weaviate' not in sys.modules:
            fake_weaviate = types.ModuleType('weaviate')

            class FakeObj:

                def __init__(self):
                    self.uuid = 'uuid-1'
                    self.metadata = types.SimpleNamespace(distance=None)
                    self.properties = {'p': 1}

            class FakeQueryResult:

                def __init__(self):
                    self.objects = [FakeObj()]

            class FakeCollectionQuery:

                def near_vector(self, *, near_vector: list, limit: int):
                    return FakeQueryResult()

            class FakeBatch:

                def add_object(self, *, properties: dict, vector: list):
                    self.added.append({'properties': properties, 'vector': vector})

                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc, tb):
                    return False

            class FakeBatchMgr:

                def dynamic(self):
                    b = FakeBatch()
                    b.added = []
                    return b

            class FakeCollection:

                def __init__(self):
                    self.query = FakeCollectionQuery()
                    self.batch = FakeBatchMgr()

            class FakeCollections:

                def __init__(self):
                    self._cols: dict[str, FakeCollection] = {}
                    self.deleted: list[str] = []

                def get(self, name: str) -> FakeCollection:
                    if name not in self._cols:
                        self._cols[name] = FakeCollection()
                    return self._cols[name]

                def delete(self, name: str):
                    self.deleted.append(name)

            class FakeWeaviateClient:

                def __init__(self):
                    self.collections = FakeCollections()
            fake_weaviate.connect_to_local = lambda host, port, grpc_port: FakeWeaviateClient()
            fake_weaviate.connect_to_weaviate_cloud = lambda cluster_url, auth_credentials: FakeWeaviateClient()
            fake_weaviate.auth = types.SimpleNamespace(AuthApiKey=lambda api_key: api_key)
            sys.modules['weaviate'] = fake_weaviate
        store = WeaviateVectorStore(url='http://weaviate', api_key=None)
        store.upsert('idx', [('id1', [0.1], {'p': 2}), ('id2', [0.2], None)])
        hits = store.query('idx', [0.1], top_k=3)
        assert hits[0][0] == 'uuid-1'
        assert hits[0][2] == {'p': 1}
        store.delete_index('idx')

    def test_pinecone_backend_upsert_query_and_delete(self, monkeypatch):
        from vectors.pinecone_backend import PineconeVectorStore
        if 'pinecone' not in sys.modules:
            fake_pinecone = types.ModuleType('pinecone')
            fake_pinecone.Pinecone = lambda api_key: types.SimpleNamespace(Index=lambda index_name: types.SimpleNamespace(upsert=lambda vectors: None, query=lambda **kw: types.SimpleNamespace(matches=[])), delete_index=lambda index_name: None)
            sys.modules['pinecone'] = fake_pinecone
        store = PineconeVectorStore(api_key='pc', environment=None, index_name='main-index')
        store.upsert('main-index', [('id1', [0.1], {'m': 1})])
        hits = store.query('main-index', [0.1], top_k=2, filter={'type': 'x'})
        assert hits == []
        store.delete_index('main-index')

    def test_build_vector_store_unknown_backend_returns_none(self, monkeypatch):
        from vectors import base as vector_base

        class FakeCfg:

            def __init__(self):
                self.pinecone = types.SimpleNamespace(enabled=False, api_key=None, environment=None, index_name='idx')
                self.qdrant = types.SimpleNamespace(enabled=False, url=None, api_key=None)
                self.weaviate = types.SimpleNamespace(enabled=False, url=None, api_key=None)
        monkeypatch.setattr(vector_base, 'VectorsConfiguration', lambda: types.SimpleNamespace(get_config=lambda: FakeCfg()), raising=True)
        assert vector_base.build_vector_store('does-not-exist') is None

    def test_vector_backend_constructors_raise_runtime_error_when_dependency_missing(self, monkeypatch):
        from vectors.pinecone_backend import PineconeVectorStore
        from vectors.qdrant_backend import QdrantVectorStore
        from vectors.weaviate_backend import WeaviateVectorStore
        real_import = builtins.__import__

        def _deny_import(name, *args, **kwargs):
            if name in {'pinecone', 'qdrant_client', 'weaviate'}:
                raise ImportError(name)
            return real_import(name, *args, **kwargs)
        monkeypatch.setattr(builtins, '__import__', _deny_import)
        with pytest.raises(RuntimeError):
            PineconeVectorStore(api_key='pc')
        with pytest.raises(RuntimeError):
            QdrantVectorStore(url='http://qdrant')
        with pytest.raises(RuntimeError):
            WeaviateVectorStore(url='http://weaviate', api_key='x')

    def test_weaviate_backend_api_key_uses_cloud_connection(self):
        from vectors.weaviate_backend import WeaviateVectorStore
        calls: dict[str, Any] = {}
        fake_weaviate = types.ModuleType('weaviate')

        class FakeWeaviateClient:

            def __init__(self):
                self.collections = types.SimpleNamespace(get=lambda name: types.SimpleNamespace(batch=types.SimpleNamespace(dynamic=lambda: None), query=types.SimpleNamespace(near_vector=lambda **kw: types.SimpleNamespace(objects=[]))), delete=lambda name: None)

        class FakeAuth:

            @staticmethod
            def AuthApiKey(api_key: str):
                return api_key

        def connect_to_cloud(*, cluster_url: str, auth_credentials: Any):
            calls['cluster_url'] = cluster_url
            calls['auth_credentials'] = auth_credentials
            return FakeWeaviateClient()
        fake_weaviate.connect_to_weaviate_cloud = connect_to_cloud
        fake_weaviate.connect_to_local = lambda host, port, grpc_port: FakeWeaviateClient()
        fake_weaviate.auth = types.SimpleNamespace(AuthApiKey=FakeAuth.AuthApiKey)
        sys.modules['weaviate'] = fake_weaviate
        store = WeaviateVectorStore(url='https://weaviate.example.com:443', api_key='apikey')
        assert calls['auth_credentials'] == 'apikey'
        assert calls['cluster_url'] == 'weaviate.example.com'
