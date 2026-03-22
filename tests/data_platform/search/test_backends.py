from tests.data_platform.search.abstraction import ISearchTests
import builtins
import sys
import types
from typing import Any, List, Optional
import pytest

def _install_module(name: str, module_obj: types.ModuleType) -> None:
    sys.modules[name] = module_obj

class TestBackends(ISearchTests):

    def test_build_search_backend_meilisearch_and_methods(self, monkeypatch):
        from search import base as search_base

        class FakeIndex:

            def __init__(self):
                self.added: list[tuple[str, list[dict[str, Any]]]] = []
                self.last_search: dict[str, Any] = {}

            def add_documents(self, documents: List[dict[str, Any]]):
                self.added.append(('default', documents))

            def search(self, query: str, **kwargs: Any):
                self.last_search = {'query': query, **kwargs}
                hits: list[dict[str, Any]] = [{'id': 1}, {'id': 2}]
                if kwargs.get('attributesToHighlight'):
                    hits[0]['_formatted'] = {'title': '<em>w</em>idget'}
                out: dict[str, Any] = {'hits': hits, 'estimatedTotalHits': 2}
                if kwargs.get('facets'):
                    out['facetDistribution'] = {'genre': {'a': 1, 'b': 1}}
                return out

        class FakeMeiliClient:

            def __init__(self, url: str, api_key: Optional[str]=None):
                self.url = url
                self.api_key = api_key
                self._index = FakeIndex()

            def index(self, index_name: str) -> FakeIndex:
                return self._index

            def delete_index(self, index_name: str) -> None:
                self.deleted = index_name
        fake_mod = types.ModuleType('meilisearch')
        fake_mod.Client = FakeMeiliClient
        _install_module('meilisearch', fake_mod)

        class FakeCfg:

            def __init__(self):
                self.meilisearch = types.SimpleNamespace(enabled=True, url='http://localhost:7700', api_key='k')
                self.typesense = types.SimpleNamespace(enabled=False)
                self.opensearch = types.SimpleNamespace(enabled=False)
        monkeypatch.setattr(search_base, 'SearchConfiguration', lambda: types.SimpleNamespace(get_config=lambda: FakeCfg()), raising=True)
        backend = search_base.build_search_backend('meilisearch')
        assert backend is not None
        docs = [{'a': 1}]
        backend.index_documents('products', docs)
        hits = backend.search('products', 'widget', limit=10, offset=5, filter={'type': 'x'})
        assert hits == [{'id': 1}, {'id': 2}]
        fr = backend.search_faceted('products', 'widget', limit=10, offset=5, facet_fields=['genre'])
        assert len(fr.hits) == 2
        assert fr.total == 2
        assert 'genre' in fr.facets
        assert len(fr.facets['genre']) == 2
        fr_hl = backend.search_faceted('products', 'widget', limit=10, offset=5, highlight_fields=['title'])
        assert fr_hl.hits[0].highlights is not None
        assert 'title' in fr_hl.hits[0].highlights
        backend.delete_index('products')

    def test_build_search_backend_returns_none_when_disabled(self, monkeypatch):
        from search import base as search_base

        class FakeCfg:

            def __init__(self):
                self.meilisearch = types.SimpleNamespace(enabled=False, url='http://localhost:7700', api_key=None)
                self.typesense = types.SimpleNamespace(enabled=False)
                self.opensearch = types.SimpleNamespace(enabled=False)
        monkeypatch.setattr(search_base, 'SearchConfiguration', lambda: types.SimpleNamespace(get_config=lambda: FakeCfg()), raising=True)
        assert search_base.build_search_backend('meilisearch') is None
        assert search_base.build_search_backend('typesense') is None
        assert search_base.build_search_backend('opensearch') is None

    def test_opensearch_backend_index_search_delete_and_filter(self, monkeypatch):
        from search.opensearch_backend import OpenSearchBackend
        calls: dict[str, Any] = {}

        class FakeClient:

            def __init__(self, **kwargs):
                calls['init_kwargs'] = kwargs

            def index(self, *, index: str, body: dict[str, Any], id: str, refresh: bool):
                calls.setdefault('index_calls', []).append({'index': index, 'body': body, 'id': id, 'refresh': refresh})

            def search(self, *, index: str, body: dict[str, Any]):
                calls['last_search_body'] = body
                q = body.get('query') or {}
                if 'match_phrase_prefix' in q:
                    mp = q['match_phrase_prefix']
                    field = next(iter(mp.keys()))
                    prefix = mp[field]
                    return {'hits': {'hits': [{'_source': {field: f'{prefix} alpha'}}, {'_source': {field: f'{prefix} beta'}}], 'total': {'value': 2}}}
                hits_list: list[dict[str, Any]] = [{'_source': {'id': 1}}, {'_source': {'id': 2}}]
                if body.get('highlight') and hits_list:
                    fld = next(iter(body['highlight']['fields'].keys()))
                    hits_list[0]['highlight'] = {fld: [f'<em>{fld}</em> hit']}
                out: dict[str, Any] = {'hits': {'hits': hits_list, 'total': {'value': 2}}}
                if 'aggs' in body:
                    out['aggregations'] = {f: {'buckets': [{'key': 'x', 'doc_count': 3}]} for f in body['aggs'].keys()}
                return out

            class indices:

                @staticmethod
                def delete(*, index: str):
                    calls['deleted_index'] = index
        fake_mod = types.ModuleType('opensearchpy')
        fake_mod.OpenSearch = FakeClient
        _install_module('opensearchpy', fake_mod)
        backend = OpenSearchBackend(hosts=['http://localhost:9200'], username='u', password='p')
        backend.index_documents('products', [{'name': 'x'}, {'id': 'doc-2', 'name': 'y'}])
        hits = backend.search('products', 'query', limit=3, offset=2, filter={'category': 'books'})
        assert hits == [{'id': 1}, {'id': 2}]
        assert 'bool' in calls['last_search_body']['query']
        assert calls['last_search_body']['from'] == 2
        assert calls['last_search_body']['size'] == 3
        fr = backend.search_faceted('products', 'query', limit=3, offset=2, filter={'category': 'books'}, facet_fields=['category'])
        assert fr.total == 2
        assert 'category' in fr.facets
        fr_hl = backend.search_faceted('products', 'query', limit=3, offset=0, highlight_fields=['title'])
        assert fr_hl.hits[0].highlights is not None
        assert 'title' in fr_hl.hits[0].highlights
        assert backend.suggest('products', 'wid', field='title', limit=5) == ['wid alpha', 'wid beta']
        backend.delete_index('products')
        assert calls['deleted_index'] == 'products'

    def test_typesense_backend_index_search_delete_and_filter(self, monkeypatch):
        from search.typesense_backend import TypesenseBackend, _filter_str
        calls: dict[str, Any] = {}

        class FakeDocuments:

            def upsert(self, d: dict[str, Any]):
                calls.setdefault('upserts', []).append(d)

            def search(self, body: dict[str, Any]):
                calls['last_search_body'] = body
                hits: list[dict[str, Any]] = [{'document': {'id': 'a'}}, {'document': {'id': 'b'}}]
                if body.get('highlight_fields'):
                    hits[0]['highlight'] = {'title': ['<em>widget</em>']}
                out: dict[str, Any] = {'hits': hits, 'found': 2}
                if body.get('facet_by'):
                    out['facet_counts'] = [{'field_name': 'k', 'counts': [{'count': 2, 'value': 'v'}]}, {'counts': []}, {'fieldName': 'alt', 'counts': [{'count': 1, 'value': 'z'}]}]
                return out

        class FakeCollection:

            def __init__(self):
                self.documents = FakeDocuments()

            def delete(self):
                calls['deleted_collection'] = True

        class FakeCollections:

            def __init__(self):
                self._cols: dict[str, FakeCollection] = {}

            def __getitem__(self, name: str) -> FakeCollection:
                if name not in self._cols:
                    self._cols[name] = FakeCollection()
                return self._cols[name]

        class FakeTypesenseClient:

            def __init__(self, cfg):
                calls['client_cfg'] = cfg
                self.collections = FakeCollections()
        fake_mod = types.ModuleType('typesense')
        fake_mod.Client = FakeTypesenseClient
        _install_module('typesense', fake_mod)
        backend = TypesenseBackend(host='localhost', port=8108, protocol='http', api_key=None)
        backend.index_documents('products', [{'name': 'x'}, {'name': 'y'}])
        hits = backend.search('products', 'widget', limit=10, offset=20, filter={'k': 'v'})
        assert hits == [{'id': 'a'}, {'id': 'b'}]
        assert _filter_str({'k': 'v'}) == 'k:v'
        assert calls['last_search_body']['filter_by'] == 'k:v'
        fr = backend.search_faceted('products', 'widget', limit=10, offset=20, filter={'k': 'v'}, facet_fields=['k'])
        assert fr.total == 2
        assert 'k' in fr.facets
        fr_hl = backend.search_faceted('products', 'widget', limit=10, offset=20, highlight_fields=['title'])
        assert fr_hl.hits[0].highlights is not None
        assert 'title' in fr_hl.hits[0].highlights
        backend.delete_index('products')
        assert calls.get('deleted_collection') is True

    def test_backend_constructors_raise_runtime_error_when_dependency_missing(self, monkeypatch):
        from search.meilisearch_backend import MeilisearchBackend
        from search.opensearch_backend import OpenSearchBackend
        from search.typesense_backend import TypesenseBackend
        real_import = builtins.__import__

        def _deny_import(name, *args, **kwargs):
            if name in {'meilisearch', 'opensearchpy', 'typesense'}:
                raise ImportError(name)
            return real_import(name, *args, **kwargs)
        monkeypatch.setattr(builtins, '__import__', _deny_import)
        with pytest.raises(RuntimeError):
            MeilisearchBackend(url='http://localhost:7700')
        with pytest.raises(RuntimeError):
            OpenSearchBackend(hosts=['http://localhost:9200'])
        with pytest.raises(RuntimeError):
            TypesenseBackend(host='localhost', port=8108, protocol='http', api_key=None)

    def test_build_search_backend_import_error_returns_none(self, monkeypatch):
        from search import base as search_base

        class FakeCfg:

            def __init__(self):
                self.meilisearch = types.SimpleNamespace(enabled=True, url='http://localhost:7700', api_key='k')
                self.typesense = types.SimpleNamespace(enabled=True, host='localhost', port=8108, protocol='http', api_key='k')
                self.opensearch = types.SimpleNamespace(enabled=True, hosts=['http://localhost:9200'], username=None, password=None)
        monkeypatch.setattr(search_base, 'SearchConfiguration', lambda: types.SimpleNamespace(get_config=lambda: FakeCfg()), raising=True)
        real_import = builtins.__import__

        def _fail_specific_backend_import(name, *args, **kwargs):
            if 'meilisearch_backend' in name or 'typesense_backend' in name or 'opensearch_backend' in name:
                raise ImportError(name)
            return real_import(name, *args, **kwargs)
        monkeypatch.setattr(builtins, '__import__', _fail_specific_backend_import)
        sys.modules.pop('search.meilisearch_backend', None)
        sys.modules.pop('search.typesense_backend', None)
        sys.modules.pop('search.opensearch_backend', None)
        assert search_base.build_search_backend('meilisearch') is None
        assert search_base.build_search_backend('typesense') is None
        assert search_base.build_search_backend('opensearch') is None

    def test_isearch_backend_abstract_methods_raise_not_implemented(self):
        from search.base import ISearchBackend

        class DummyBackend(ISearchBackend):
            name = 'dummy'

            def index_documents(self, index_name: str, documents: List[dict[str, Any]]) -> None:
                return super().index_documents(index_name=index_name, documents=documents)

            def search(self, index_name: str, query: str, *, limit: int=20, offset: int=0, filter: Optional[dict[str, Any]]=None, highlight_fields: Optional[List[str]]=None):
                return super().search(index_name=index_name, query=query, limit=limit, offset=offset, filter=filter, highlight_fields=highlight_fields)

            def delete_index(self, index_name: str) -> None:
                return super().delete_index(index_name=index_name)
        b = DummyBackend()
        with pytest.raises(NotImplementedError):
            b.index_documents('i', [{'a': 1}])
        with pytest.raises(NotImplementedError):
            b.search('i', 'q')
        with pytest.raises(NotImplementedError):
            b.delete_index('i')
        with pytest.raises(NotImplementedError):
            b.search_faceted('i', 'q')
