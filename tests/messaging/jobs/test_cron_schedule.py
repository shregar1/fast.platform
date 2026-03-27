"""Module test_cron_schedule.py."""

from __future__ import annotations

"""Tests for :mod:`messaging.jobs.schedule` (cron DTO and Celery crontab)."""
import pytest

from messaging.jobs.schedule import CronScheduleDTO, celery_crontab_schedule, parse_cron_fields
from tests.messaging.jobs.abstraction import IJobTests


class TestCronSchedule(IJobTests):
    """Represents the TestCronSchedule class."""

    def test_cron_schedule_dto(self) -> None:
        """Execute test_cron_schedule_dto operation.

        Returns:
            The result of the operation.
        """
        s = CronScheduleDTO("0 9 * * *", timezone="America/New_York")
        assert parse_cron_fields(s.expression) == ("0", "9", "*", "*", "*")
        with pytest.raises(ValueError):
            CronScheduleDTO("invalid")

    def test_celery_crontab_schedule(self) -> None:
        """Execute test_celery_crontab_schedule operation.

        Returns:
            The result of the operation.
        """
        pytest.importorskip("celery")
        c = celery_crontab_schedule(CronScheduleDTO("0 9 * * *"))
        assert c.__class__.__name__ == "crontab"
