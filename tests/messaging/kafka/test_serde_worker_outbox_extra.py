"""Module test_serde_worker_outbox_extra.py."""

from __future__ import annotations

"""Extra coverage: serde, worker, outbox exception path."""
import asyncio
import contextlib
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from tests.messaging.kafka.abstraction import IKafkaTests


class TestSerdeWorkerOutboxExtra(IKafkaTests):
    """Represents the TestSerdeWorkerOutboxExtra class."""

    def test_serialize_protobuf_missing_method(self) -> None:
        """Execute test_serialize_protobuf_missing_method operation.

        Returns:
            The result of the operation.
        """
        from messaging.kafka.serde import serialize_protobuf

        with pytest.raises(TypeError, match="SerializeToString"):
            serialize_protobuf(object())

    def test_serialize_protobuf_ok(self) -> None:
        """Execute test_serialize_protobuf_ok operation.

        Returns:
            The result of the operation.
        """
        from messaging.kafka.serde import serialize_protobuf

        m = SimpleNamespace(SerializeToString=lambda: b"\x01\x02")
        assert serialize_protobuf(m) == b"\x01\x02"

    def test_serialize_avro_record_when_fastavro_installed(self) -> None:
        """Execute test_serialize_avro_record_when_fastavro_installed operation.

        Returns:
            The result of the operation.
        """
        pytest.importorskip("fastavro")
        from messaging.kafka.serde import serialize_avro_record

        schema = {"type": "record", "name": "R", "fields": [{"name": "n", "type": "int"}]}
        out = serialize_avro_record({"n": 1}, schema)
        assert isinstance(out, bytes) and len(out) > 0

    @pytest.mark.asyncio
    async def test_handle_message(self) -> None:
        """Execute test_handle_message operation.

        Returns:
            The result of the operation.
        """
        from messaging.kafka.worker import handle_message

        await handle_message("topic", b"hello")

    def test_worker_run_invokes_asyncio_run(self) -> None:
        """Execute test_worker_run_invokes_asyncio_run operation.

        Returns:
            The result of the operation.
        """
        with patch("fast_platform.messaging.kafka.worker.asyncio.run") as ar:
            from messaging.kafka.worker import run

            run()
            ar.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_outbox_publisher_loop_logs_on_publish_failure(self) -> None:
        """Execute test_run_outbox_publisher_loop_logs_on_publish_failure operation.

        Returns:
            The result of the operation.
        """
        from messaging.kafka.outbox import OutboxMessage, run_outbox_publisher_loop

        stop = asyncio.Event()

        async def load(_limit: int) -> list[OutboxMessage]:
            """Execute load operation.

            Args:
                _limit: The _limit parameter.

            Returns:
                The result of the operation.
            """
            return [OutboxMessage(id=1, topic="t", value=b"x")]

        async def mark(_id: int) -> None:
            """Execute mark operation.

            Args:
                _id: The _id parameter.

            Returns:
                The result of the operation.
            """
            pass

        prod = MagicMock()

        async def stop_soon() -> None:
            """Execute stop_soon operation.

            Returns:
                The result of the operation.
            """
            await asyncio.sleep(0.15)
            stop.set()

        with patch(
            "fast_platform.messaging.kafka.outbox.publish_outbox_batch", side_effect=RuntimeError("send failed")
        ):
            asyncio.create_task(stop_soon())
            task = asyncio.create_task(
                run_outbox_publisher_loop(
                    prod, load, mark, limit=5, interval_seconds=0.01, stop_event=stop
                )
            )
            await asyncio.wait_for(stop.wait(), timeout=3.0)
            task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task
