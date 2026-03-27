"""Portable cron schedule DTO for Celery Beat, RQ Scheduler, and Dramatiq (periodic tasks)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Tuple

_CRON5 = re.compile(r"^(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)$")


@dataclass(frozen=True)
class CronScheduleDTO:
    """Five-field cron string (minute, hour, day-of-month, month, day-of-week), plus IANA timezone.

    Examples: ``0 9 * * 1-5`` (weekdays 09:00), ``*/15 * * * *`` (every 15 minutes).
    """

    expression: str
    timezone: str = "UTC"

    def __post_init__(self) -> None:
        """Execute __post_init__ operation.

        Returns:
            The result of the operation.
        """
        expr = self.expression.strip()
        if not _CRON5.match(expr):
            raise ValueError(
                "expression must contain exactly 5 whitespace-separated cron fields: "
                "minute hour day-of-month month day-of-week",
            )


def parse_cron_fields(expression: str) -> Tuple[str, str, str, str, str]:
    """Split a validated 5-field cron string into its parts."""
    m = _CRON5.match(expression.strip())
    if not m:
        raise ValueError("invalid cron expression")
    return m.group(1), m.group(2), m.group(3), m.group(4), m.group(5)


def celery_crontab_schedule(dto: CronScheduleDTO) -> Any:
    """Build a :class:`celery.schedules.crontab` from ``dto`` (requires ``fast_jobs[celery]``).

    Uses :meth:`celery.schedules.crontab.from_string`, whose five fields are
    ``minute hour day_of_month month_of_year day_of_week`` (same layout as this DTO).
    Set Celery Beat / app ``timezone`` to :attr:`CronScheduleDTO.timezone` so schedules align.
    """
    try:
        from celery.schedules import crontab
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("celery is not installed. pip install fast_jobs[celery]") from e

    _ = parse_cron_fields(dto.expression)
    return crontab.from_string(dto.expression.strip())


def rq_scheduler_cron(dto: CronScheduleDTO) -> str:
    """Return the same 5-field expression for `rq-scheduler`_ / cron-style workers.

    .. _rq-scheduler: https://github.com/rq/rq-scheduler
    """
    _ = parse_cron_fields(dto.expression)
    return dto.expression.strip()


def dramatiq_periodiq_cron(dto: CronScheduleDTO) -> str:
    """Cron string suitable for ``dramatiq-periodiq`` / similar periodic schedulers.

    Timezone should be applied in the scheduler process (set ``TZ`` or scheduler config).
    """
    _ = parse_cron_fields(dto.expression)
    return dto.expression.strip()
