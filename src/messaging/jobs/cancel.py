"""
Cancel in-flight jobs where the backend supports it.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Optional


@dataclass(frozen=True)
class CancelJobResult:
    """Outcome of :func:`cancel_job`."""

    cancelled: bool
    backend: Literal["celery", "rq", "dramatiq"]
    detail: Optional[str] = None


def cancel_job(
    job_id: str,
    backend: Literal["celery", "rq", "dramatiq"],
    *,
    celery_app: Any = None,
    rq_connection: Any = None,
    terminate: bool = True,
) -> CancelJobResult:
    """
    Request cancellation of a job.

    - **celery** — ``control.revoke`` with optional ``terminate`` (SIGTERM workers).
    - **rq** — ``Job.cancel()`` on the fetched job (requires ``rq_connection``).
    - **dramatiq** — not supported in core; returns ``cancelled=False`` (use ``dramatiq-abort``
      or broker-specific tooling).
    """
    if backend == "celery":
        return _cancel_celery(job_id, celery_app, terminate=terminate)
    if backend == "rq":
        return _cancel_rq(job_id, rq_connection)
    if backend == "dramatiq":
        return CancelJobResult(
            cancelled=False,
            backend="dramatiq",
            detail="Dramatiq has no generic cancel in core; use dramatiq-abort middleware or delete/requeue via Redis.",
        )
    raise ValueError(f"unknown backend: {backend}")


def _cancel_celery(job_id: str, celery_app: Any, *, terminate: bool) -> CancelJobResult:
    try:
        from celery.result import AsyncResult
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("celery is not installed. pip install fast_jobs[celery]") from e

    if celery_app is None:
        from messaging.jobs.celery_app import make_celery_app

        celery_app = make_celery_app()

    AsyncResult(job_id, app=celery_app).revoke(terminate=terminate)
    return CancelJobResult(cancelled=True, backend="celery", detail=None)


def _cancel_rq(job_id: str, rq_connection: Any) -> CancelJobResult:
    try:
        from rq.job import Job
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("rq is not installed. pip install fast_jobs[rq]") from e

    if rq_connection is None:
        raise ValueError("rq_connection is required for backend='rq'")

    job = Job.fetch(job_id, connection=rq_connection)
    job.cancel()
    return CancelJobResult(cancelled=True, backend="rq", detail=None)
