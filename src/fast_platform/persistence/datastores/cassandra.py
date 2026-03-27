"""Cassandra wide-column store implementation.

Provides a thin wrapper around the `cassandra-driver` library implementing
the `IWideColumnStore` interface.
"""

from typing import Any, Iterable, Optional

from loguru import logger

from .interfaces import IWideColumnStore

try:  # Optional dependency
    from cassandra.cluster import Cluster  # type: ignore
except Exception:  # pragma: no cover - optional import
    Cluster = None  # type: ignore[misc, assignment]


class CassandraWideColumnStore(IWideColumnStore):
    """Cassandra-backed wide-column store."""

    def __init__(
        self,
        contact_points: Iterable[str] | None = None,
        port: int = 9042,
        keyspace: Optional[str] = None,
    ) -> None:
        """Execute __init__ operation.

        Args:
            contact_points: The contact_points parameter.
            port: The port parameter.
            keyspace: The keyspace parameter.
        """
        self._contact_points = list(contact_points or ["127.0.0.1"])
        self._port = port
        self._keyspace = keyspace
        self._cluster: Any = None
        self._session: Any = None

    def connect(self) -> None:
        """Execute connect operation.

        Returns:
            The result of the operation.
        """
        if Cluster is None:  # pragma: no cover - guarded by optional import
            raise RuntimeError(
                "cassandra-driver is not installed. Install it with `pip install cassandra-driver`."
            )
        self._cluster = Cluster(self._contact_points, port=self._port)
        if self._keyspace:
            self._session = self._cluster.connect(self._keyspace)
        else:
            self._session = self._cluster.connect()
        logger.info(
            "Connected CassandraWideColumnStore",
            contact_points=self._contact_points,
            port=self._port,
            keyspace=self._keyspace,
        )

    def disconnect(self) -> None:
        """Execute disconnect operation.

        Returns:
            The result of the operation.
        """
        if self._session is not None:
            self._session.shutdown()
            self._session = None
        if self._cluster is not None:
            self._cluster.shutdown()
            self._cluster = None
        logger.info("Disconnected CassandraWideColumnStore")

    def get_session(self) -> Any:
        """Execute get_session operation.

        Returns:
            The result of the operation.
        """
        if self._session is None:
            raise RuntimeError("CassandraWideColumnStore is not connected.")
        return self._session

    def execute(self, query: str, parameters: Any | None = None) -> Any:
        """Execute execute operation.

        Args:
            query: The query parameter.
            parameters: The parameters parameter.

        Returns:
            The result of the operation.
        """
        session = self.get_session()
        if parameters is None:
            return session.execute(query)
        return session.execute(query, parameters)
