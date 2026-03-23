from __future__ import annotations

"""Extra coverage: serde, worker, outbox exception path."""
import asyncio
import contextlib
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from tests.messaging.kafka.abstraction import IKafkaTests


class TestSerdeWorkerOutboxExtra(IKafkaTests):
    def test_serialize_protobuf_missing_method(self) -> None:
        from messaging.kafka.serde import serialize_protobuf

        with pytest.raises(TypeError, match="SerializeToString"):
            serialize_protobuf(object())

    def test_serialize_protobuf_ok(self) -> None:
        from messaging.kafka.serde import serialize_protobuf

        m = SimpleNamespace(SerializeToString=lambda: b"\x01\x02")
        assert serialize_protobuf(m) == b"\x01\x02"

    def test_serialize_avro_record_when_fastavro_installed(self) -> None:
        pytest.importorskip("fastavro")
        from messaging.kafka.serde import serialize_avro_record

        schema = {"type": "record", "name": "R", "fields": [{"name": "n", "type": "int"}]}
        out = serialize_avro_record({"n": 1}, schema)
        assert isinstance(out, bytes) and len(out) > 0

    @pytest.mark.asyncio
    async def test_handle_message(self) -> None:
        from messaging.kafka.worker import handle_message

        await handle_message("topic", b"hello")

    def test_worker_run_invokes_asyncio_run(self) -> None:
        with patch("messaging.kafka.worker.asyncio.run") as ar:
            from messaging.kafka.worker import run

            run()
            ar.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_outbox_publisher_loop_logs_on_publish_failure(self) -> None:
        from messaging.kafka.outbox import OutboxMessage, run_outbox_publisher_loop

        stop = asyncio.Event()

        async def load(_limit: int) -> list[OutboxMessage]:
            return [OutboxMessage(id=1, topic="t", value=b"x")]

        async def mark(_id: int) -> None:
            pass

        prod = MagicMock()

        async def stop_soon() -> None:
            await asyncio.sleep(0.15)
            stop.set()

        with patch("messaging.kafka.outbox.publish_outbox_batch", side_effect=RuntimeError("send failed")):
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
