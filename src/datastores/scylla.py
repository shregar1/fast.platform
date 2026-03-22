"""
ScyllaDB wide-column store implementation.

ScyllaDB is protocol-compatible with Cassandra, so this implementation
reuses the same `cassandra-driver` under the hood but is provided as a
separate type to make dependency boundaries explicit.
"""

from typing import Any, Iterable, Optional

from loguru import logger

from fast_datastores.interfaces import IWideColumnStore

try:  # Optional dependency
    from cassandra.cluster import Cluster  # type: ignore
except Exception:  # pragma: no cover - optional import
    Cluster = None  # type: ignore[misc, assignment]


class ScyllaWideColumnStore(IWideColumnStore):
    """
    ScyllaDB-backed wide-column store.
    """

    def __init__(
        self,
        contact_points: Iterable[str] | None = None,
        port: int = 9042,
        keyspace: Optional[str] = None,
    ) -> None:
        self._contact_points = list(contact_points or ["127.0.0.1"])
        self._port = port
        self._keyspace = keyspace
        self._cluster: Any = None
        self._session: Any = None

    def connect(self) -> None:
        if Cluster is None:  # pragma: no cover - guarded by optional import
            raise RuntimeError(
                "cassandra-driver is not installed. "
                "Install it with `pip install cassandra-driver`."
            )
        self._cluster = Cluster(self._contact_points, port=self._port)
        if self._keyspace:
            self._session = self._cluster.connect(self._keyspace)
        else:
            self._session = self._cluster.connect()
        logger.info(
            "Connected ScyllaWideColumnStore",
            contact_points=self._contact_points,
            port=self._port,
            keyspace=self._keyspace,
        )

    def disconnect(self) -> None:
        if self._session is not None:
            self._session.shutdown()
            self._session = None
        if self._cluster is not None:
            self._cluster.shutdown()
            self._cluster = None
        logger.info("Disconnected ScyllaWideColumnStore")

    def get_session(self) -> Any:
        if self._session is None:
            raise RuntimeError("ScyllaWideColumnStore is not connected.")
        return self._session

    def execute(self, query: str, parameters: Any | None = None) -> Any:
        session = self.get_session()
        if parameters is None:
            return session.execute(query)
        return session.execute(query, parameters)


