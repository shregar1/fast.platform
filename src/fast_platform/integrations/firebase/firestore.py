"""Firestore integration."""

from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Document:
    """Firestore document."""

    id: str
    path: str
    data: Dict[str, Any]
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None


class FirestoreClient:
    """Google Cloud Firestore client."""

    def __init__(self, project: Optional[str] = None, credentials_path: Optional[str] = None):
        """Execute __init__ operation.

        Args:
            project: The project parameter.
            credentials_path: The credentials_path parameter.
        """
        self.project = project
        self.credentials_path = credentials_path
        self._client = None

    def _get_client(self):
        """Execute _get_client operation.

        Returns:
            The result of the operation.
        """
        if self._client is None:
            try:
                from google.cloud import firestore

                if self.credentials_path:
                    self._client = firestore.Client.from_service_account_json(
                        self.credentials_path, project=self.project
                    )
                else:
                    self._client = firestore.Client(project=self.project)

            except ImportError:
                raise ImportError("google-cloud-firestore required for FirestoreClient")

        return self._client

    async def get_document(self, collection: str, document_id: str) -> Optional[Document]:
        """Get a document by ID."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        client = self._get_client()
        doc_ref = client.collection(collection).document(document_id)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            doc = await loop.run_in_executor(pool, doc_ref.get)

        if not doc.exists:
            return None

        return Document(
            id=doc.id,
            path=doc.reference.path,
            data=doc.to_dict(),
            create_time=doc.create_time,
            update_time=doc.update_time,
        )

    async def create_document(
        self, collection: str, data: Dict[str, Any], document_id: Optional[str] = None
    ) -> Document:
        """Create a document."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        client = self._get_client()
        collection_ref = client.collection(collection)

        if document_id:
            doc_ref = collection_ref.document(document_id)
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                await loop.run_in_executor(pool, lambda: doc_ref.set(data))
        else:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as pool:
                doc_ref = await loop.run_in_executor(pool, lambda: collection_ref.add(data)[1])

        return Document(id=doc_ref.id, path=doc_ref.path, data=data)

    async def update_document(
        self, collection: str, document_id: str, data: Dict[str, Any]
    ) -> Document:
        """Update a document."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        client = self._get_client()
        doc_ref = client.collection(collection).document(document_id)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, lambda: doc_ref.update(data))

        # Get updated document
        return await self.get_document(collection, document_id)

    async def delete_document(self, collection: str, document_id: str) -> bool:
        """Delete a document."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        client = self._get_client()
        doc_ref = client.collection(collection).document(document_id)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            await loop.run_in_executor(pool, doc_ref.delete)

        return True

    async def query(
        self,
        collection: str,
        filters: Optional[List[tuple]] = None,
        order_by: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[Document]:
        """Query documents."""
        import asyncio
        from concurrent.futures import ThreadPoolExecutor

        client = self._get_client()
        query = client.collection(collection)

        if filters:
            for field, op, value in filters:
                query = query.where(field, op, value)

        if order_by:
            query = query.order_by(order_by)

        if limit:
            query = query.limit(limit)

        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as pool:
            docs = await loop.run_in_executor(pool, query.get)

        return [
            Document(
                id=doc.id,
                path=doc.reference.path,
                data=doc.to_dict(),
                create_time=doc.create_time,
                update_time=doc.update_time,
            )
            for doc in docs
        ]
