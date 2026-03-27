"""
Search client implementations
"""

from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod


class SearchClient(ABC):
    """Abstract search client"""
    
    @abstractmethod
    async def create_index(self, name: str, options: Dict[str, Any]) -> None:
        pass
    
    @abstractmethod
    async def delete_index(self, name: str) -> None:
        pass
    
    @abstractmethod
    async def add_documents(
        self,
        index: str,
        documents: List[Dict[str, Any]]
    ) -> None:
        pass
    
    @abstractmethod
    async def update_documents(
        self,
        index: str,
        documents: List[Dict[str, Any]]
    ) -> None:
        pass
    
    @abstractmethod
    async def delete_document(self, index: str, document_id: str) -> None:
        pass
    
    @abstractmethod
    async def search(
        self,
        index: str,
        query: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        pass


class MeilisearchClient(SearchClient):
    """Meilisearch client"""
    
    def __init__(self, url: str = "http://localhost:7700", api_key: Optional[str] = None):
        self.url = url
        self.api_key = api_key
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                import meilisearch
                self._client = meilisearch.Client(self.url, self.api_key)
            except ImportError:
                raise ImportError("meilisearch package required for MeilisearchClient")
        return self._client
    
    async def create_index(self, name: str, options: Dict[str, Any]) -> None:
        client = self._get_client()
        try:
            client.create_index(name, options)
        except Exception:
            pass  # Index might already exist
    
    async def delete_index(self, name: str) -> None:
        client = self._get_client()
        client.index(name).delete()
    
    async def add_documents(
        self,
        index: str,
        documents: List[Dict[str, Any]]
    ) -> None:
        client = self._get_client()
        client.index(index).add_documents(documents)
    
    async def update_documents(
        self,
        index: str,
        documents: List[Dict[str, Any]]
    ) -> None:
        client = self._get_client()
        client.index(index).update_documents(documents)
    
    async def delete_document(self, index: str, document_id: str) -> None:
        client = self._get_client()
        client.index(index).delete_document(document_id)
    
    async def search(
        self,
        index: str,
        query: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        client = self._get_client()
        search_params = {
            "q": query,
            **options
        }
        return client.index(index).search(query, search_params)


class TypesenseClient(SearchClient):
    """Typesense client"""
    
    def __init__(
        self,
        api_key: str,
        nodes: List[Dict[str, str]]
    ):
        self.api_key = api_key
        self.nodes = nodes
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                import typesense
                self._client = typesense.Client({
                    "api_key": self.api_key,
                    "nodes": self.nodes
                })
            except ImportError:
                raise ImportError("typesense package required for TypesenseClient")
        return self._client
    
    async def create_index(self, name: str, options: Dict[str, Any]) -> None:
        client = self._get_client()
        schema = {
            "name": name,
            "fields": options.get("fields", []),
            **options
        }
        try:
            client.collections.create(schema)
        except Exception:
            pass
    
    async def delete_index(self, name: str) -> None:
        client = self._get_client()
        client.collections[name].delete()
    
    async def add_documents(
        self,
        index: str,
        documents: List[Dict[str, Any]]
    ) -> None:
        client = self._get_client()
        client.collections[index].documents.import_(documents)
    
    async def update_documents(
        self,
        index: str,
        documents: List[Dict[str, Any]]
    ) -> None:
        client = self._get_client()
        for doc in documents:
            client.collections[index].documents[doc["id"]].update(doc)
    
    async def delete_document(self, index: str, document_id: str) -> None:
        client = self._get_client()
        client.collections[index].documents[document_id].delete()
    
    async def search(
        self,
        index: str,
        query: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        client = self._get_client()
        search_params = {
            "q": query,
            "query_by": options.get("query_by", "*"),
            **options
        }
        return client.collections[index].documents.search(search_params)


class ElasticsearchClient(SearchClient):
    """Elasticsearch client"""
    
    def __init__(self, hosts: List[str] = None):
        self.hosts = hosts or ["http://localhost:9200"]
        self._client = None
    
    def _get_client(self):
        if self._client is None:
            try:
                from elasticsearch import AsyncElasticsearch
                self._client = AsyncElasticsearch(hosts=self.hosts)
            except ImportError:
                raise ImportError("elasticsearch package required for ElasticsearchClient")
        return self._client
    
    async def create_index(self, name: str, options: Dict[str, Any]) -> None:
        client = self._get_client()
        await client.indices.create(index=name, body=options)
    
    async def delete_index(self, name: str) -> None:
        client = self._get_client()
        await client.indices.delete(index=name, ignore=[404])
    
    async def add_documents(
        self,
        index: str,
        documents: List[Dict[str, Any]]
    ) -> None:
        client = self._get_client()
        await client.bulk(
            body=[
                {"index": {"_index": index, "_id": doc.get("id")}}
                if "id" in doc else {"index": {"_index": index}}
                for doc in documents
                for _ in [doc]
            ]
        )
    
    async def update_documents(
        self,
        index: str,
        documents: List[Dict[str, Any]]
    ) -> None:
        client = self._get_client()
        for doc in documents:
            doc_id = doc.pop("id", None)
            if doc_id:
                await client.update(index=index, id=doc_id, body={"doc": doc})
    
    async def delete_document(self, index: str, document_id: str) -> None:
        client = self._get_client()
        await client.delete(index=index, id=document_id)
    
    async def search(
        self,
        index: str,
        query: str,
        options: Dict[str, Any]
    ) -> Dict[str, Any]:
        client = self._get_client()
        body = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": options.get("fields", ["*"])
                }
            },
            **options
        }
        return await client.search(index=index, body=body)
