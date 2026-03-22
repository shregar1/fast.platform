from __future__ import annotations

"""Tests for :mod:`jobs.schedule` (cron DTO and Celery crontab)."""
import pytest

from jobs.schedule import CronScheduleDTO, celery_crontab_schedule, parse_cron_fields
from tests.messaging.jobs.abstraction import IJobTests


class TestCronSchedule(IJobTests):
    def test_cron_schedule_dto(self) -> None:
        s = CronScheduleDTO("0 9 * * *", timezone="America/New_York")
        assert parse_cron_fields(s.expression) == ("0", "9", "*", "*", "*")
        with pytest.raises(ValueError):
            CronScheduleDTO("invalid")

    def test_celery_crontab_schedule(self) -> None:
        pytest.importorskip("celery")
        c = celery_crontab_schedule(CronScheduleDTO("0 9 * * *"))
        assert c.__class__.__name__ == "crontab"
