"""
Elasticsearch search store implementation.

Provides a thin wrapper around the official `elasticsearch` client that
implements the `ISearchStore` interface.
"""

from typing import Any, Dict, Iterable, Optional

from loguru import logger

from .interfaces import ISearchStore

try:  # Optional dependency
    from elasticsearch import Elasticsearch  # type: ignore
except Exception:  # pragma: no cover - optional import
    Elasticsearch = None  # type: ignore[misc, assignment]


class ElasticsearchSearchStore(ISearchStore):
    """
    Elasticsearch-backed search store.
    """

    def __init__(
        self,
        hosts: Iterable[str] | None = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify_certs: bool = True,
    ) -> None:
        self._hosts = list(hosts or ["http://localhost:9200"])
        self._username = username
        self._password = password
        self._verify_certs = verify_certs
        self._client: Any = None

    @property
    def client(self) -> Any:
        if self._client is None:
            raise RuntimeError("ElasticsearchSearchStore is not connected.")
        return self._client

    def connect(self) -> None:
        if Elasticsearch is None:  # pragma: no cover - guarded by optional import
            raise RuntimeError(
                "elasticsearch client is not installed. "
                "Install it with `pip install elasticsearch`."
            )
        kwargs: Dict[str, Any] = {"hosts": self._hosts}
        if self._username and self._password:
            kwargs["basic_auth"] = (self._username, self._password)
        kwargs["verify_certs"] = self._verify_certs
        self._client = Elasticsearch(**kwargs)
        logger.info("Connected ElasticsearchSearchStore", hosts=self._hosts)

    def disconnect(self) -> None:
        if self._client is not None:
            try:
                self._client.close()
            except Exception:
                pass
            self._client = None
            logger.info("Disconnected ElasticsearchSearchStore")

    def index(
        self,
        index: str,
        id: str,
        document: Dict[str, Any],
    ) -> Any:
        return self.client.index(index=index, id=id, document=document)

    def delete(self, index: str, id: str) -> Any:
        return self.client.delete(index=index, id=id, ignore=[404])

    def search(
        self,
        index: str,
        query: Dict[str, Any],
        size: int = 10,
    ) -> Dict[str, Any]:
        return self.client.search(index=index, query=query, size=size)

    def ping(self) -> bool:
        try:
            return bool(self.client.ping())
        except Exception as exc:  # pragma: no cover
            logger.error(f"Elasticsearch ping failed: {exc}")
            return False

