from __future__ import annotations

"""Tests for :mod:`jobs.cancel` (mocked backends)."""
from unittest.mock import MagicMock, patch

from jobs.cancel import CancelJobResult, cancel_job
from tests.messaging.jobs.abstraction import IJobTests


class TestCancelJob(IJobTests):
    def test_cancel_dramatiq_unsupported(self) -> None:
        r = cancel_job("mid", "dramatiq")
        assert isinstance(r, CancelJobResult)
        assert r.cancelled is False
        assert r.backend == "dramatiq"

    @patch("celery.result.AsyncResult")
    @patch("jobs.celery_app.make_celery_app")
    def test_cancel_celery(self, _mock_make: MagicMock, mock_ar_cls: MagicMock) -> None:
        mock_inst = MagicMock()
        mock_ar_cls.return_value = mock_inst
        r = cancel_job("jid", "celery")
        assert r.cancelled is True
        mock_inst.revoke.assert_called_once()

    @patch("rq.job.Job")
    def test_cancel_rq(self, mock_job_cls: MagicMock) -> None:
        mock_job = MagicMock()
        mock_job_cls.fetch.return_value = mock_job
        conn = MagicMock()
        r = cancel_job("jid", "rq", rq_connection=conn)
        assert r.cancelled is True
        mock_job.cancel.assert_called_once()
