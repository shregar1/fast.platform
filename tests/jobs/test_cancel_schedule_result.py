"""Tests for cancel_job, CronScheduleDTO, and get_job_status (mocked)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from jobs.cancel import CancelJobResult, cancel_job
from jobs.result import JobStatus, get_job_status
from jobs.schedule import CronScheduleDTO, celery_crontab_schedule, parse_cron_fields


def test_cancel_dramatiq_unsupported():
    r = cancel_job("mid", "dramatiq")
    assert isinstance(r, CancelJobResult)
    assert r.cancelled is False
    assert r.backend == "dramatiq"


@patch("celery.result.AsyncResult")
@patch("jobs.celery_app.make_celery_app")
def test_cancel_celery(_mock_make: MagicMock, mock_ar_cls: MagicMock) -> None:
    mock_inst = MagicMock()
    mock_ar_cls.return_value = mock_inst
    r = cancel_job("jid", "celery")
    assert r.cancelled is True
    mock_inst.revoke.assert_called_once()


@patch("rq.job.Job")
def test_cancel_rq(mock_job_cls: MagicMock) -> None:
    mock_job = MagicMock()
    mock_job_cls.fetch.return_value = mock_job
    conn = MagicMock()
    r = cancel_job("jid", "rq", rq_connection=conn)
    assert r.cancelled is True
    mock_job.cancel.assert_called_once()


def test_cron_schedule_dto():
    s = CronScheduleDTO("0 9 * * *", timezone="America/New_York")
    assert parse_cron_fields(s.expression) == ("0", "9", "*", "*", "*")
    with pytest.raises(ValueError):
        CronScheduleDTO("invalid")


def test_celery_crontab_schedule():
    pytest.importorskip("celery")
    c = celery_crontab_schedule(CronScheduleDTO("0 9 * * *"))
    assert c.__class__.__name__ == "crontab"


@patch("celery.result.AsyncResult")
@patch("jobs.celery_app.make_celery_app")
def test_get_job_status_celery(_mock_make: MagicMock, mock_ar_cls: MagicMock) -> None:
    mock_ar = MagicMock()
    mock_ar.state = "SUCCESS"
    mock_ar.result = {"ok": True}
    mock_ar_cls.return_value = mock_ar
    snap = get_job_status("jid", "celery")
    assert snap.status == JobStatus.SUCCESS
    assert snap.result == {"ok": True}
