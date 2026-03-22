from __future__ import annotations
"""Tests for :mod:`jobs.result.get_job_status` (mocked Celery)."""
from tests.messaging.jobs.abstraction import IJobTests



from unittest.mock import MagicMock, patch

from jobs.result import JobStatus, get_job_status


class TestJobStatus(IJobTests):
    @patch("celery.result.AsyncResult")
    @patch("jobs.celery_app.make_celery_app")
    def test_get_job_status_celery(self, _mock_make: MagicMock, mock_ar_cls: MagicMock) -> None:
        mock_ar = MagicMock()
        mock_ar.state = "SUCCESS"
        mock_ar.result = {"ok": True}
        mock_ar_cls.return_value = mock_ar
        snap = get_job_status("jid", "celery")
        assert snap.status == JobStatus.SUCCESS
        assert snap.result == {"ok": True}
