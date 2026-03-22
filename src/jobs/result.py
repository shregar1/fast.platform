"""
Enqueue/result DTOs and backend-agnostic job status without exposing Celery/RQ/Dramatiq types.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Literal, Optional


@dataclass
class JobEnqueueResult:
    """Return value from :func:`fast_jobs.enqueue.enqueue`."""

    job_id: str
    backend: Literal["celery", "rq", "dramatiq"]
    queue: Optional[str] = None
    timeout_seconds: Optional[int] = None
    #: Opaque backend handle (e.g. Celery ``AsyncResult``). Prefer :func:`get_job_status`.
    raw: Any = None
    #: For Dramatiq status lookup via :func:`get_job_status` (queue + actor name).
    dramatiq_queue_name: Optional[str] = None
    dramatiq_actor_name: Optional[str] = None


class JobStatus(str, Enum):
    """Normalized lifecycle for a background job."""

    PENDING = "pending"
    STARTED = "started"
    SUCCESS = "success"
    FAILURE = "failure"
    REVOKED = "revoked"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class JobStatusSnapshot:
    """Stable view of a job — no Celery ``AsyncResult`` / RQ ``Job`` in the public surface."""

    job_id: str
    backend: Literal["celery", "rq", "dramatiq"]
    status: JobStatus
    result: Any = None
    error: Optional[str] = None


def _map_celery_state(state: str) -> JobStatus:
    s = (state or "").upper()
    if s in ("PENDING",):
        return JobStatus.PENDING
    if s in ("STARTED", "RETRY"):
        return JobStatus.STARTED
    if s in ("SUCCESS",):
        return JobStatus.SUCCESS
    if s in ("FAILURE",):
        return JobStatus.FAILURE
    if s in ("REVOKED",):
        return JobStatus.REVOKED
    return JobStatus.UNKNOWN


def get_job_status(
    job_id: str,
    backend: Literal["celery", "rq", "dramatiq"],
    *,
    celery_app: Any = None,
    rq_connection: Any = None,
    dramatiq_queue_name: Optional[str] = None,
    dramatiq_actor_name: Optional[str] = None,
) -> JobStatusSnapshot:
    """
    Fetch status/result using ``job_id`` and ``backend``.

    - **celery** — optional ``celery_app``; defaults to :func:`fast_jobs.celery_app.make_celery_app`.
    - **rq** — pass Redis connection via ``rq_connection`` (required).
    - **dramatiq** — requires ``dramatiq_queue_name`` and ``dramatiq_actor_name`` (same as used at enqueue)
      and a configured ``dramatiq.results.Results`` middleware.
    """
    if backend == "celery":
        return _status_celery(job_id, celery_app)
    if backend == "rq":
        return _status_rq(job_id, rq_connection)
    if backend == "dramatiq":
        return _status_dramatiq(
            job_id, dramatiq_queue_name=dramatiq_queue_name, dramatiq_actor_name=dramatiq_actor_name
        )
    raise ValueError(f"unknown backend: {backend}")


def _status_celery(job_id: str, celery_app: Any) -> JobStatusSnapshot:
    try:
        from celery.result import AsyncResult
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("celery is not installed. pip install fast_jobs[celery]") from e

    if celery_app is None:
        from jobs.celery_app import make_celery_app

        celery_app = make_celery_app()

    ar = AsyncResult(job_id, app=celery_app)
    state = ar.state
    st = _map_celery_state(state)
    err: Optional[str] = None
    res: Any = None
    if st == JobStatus.SUCCESS:
        res = ar.result
    elif st == JobStatus.FAILURE:
        err = str(ar.result) if ar.result is not None else None
    return JobStatusSnapshot(
        job_id=job_id,
        backend="celery",
        status=st,
        result=res,
        error=err,
    )


def _status_rq(job_id: str, rq_connection: Any) -> JobStatusSnapshot:
    try:
        from rq.job import Job
        from rq.job import JobStatus as RQJobStatus
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("rq is not installed. pip install fast_jobs[rq]") from e

    if rq_connection is None:
        raise ValueError("rq_connection is required for backend='rq'")

    job = Job.fetch(job_id, connection=rq_connection)
    status_raw = job.get_status()
    err: Optional[str] = None
    res: Any = None

    if status_raw in (
        RQJobStatus.QUEUED,
        RQJobStatus.SCHEDULED,
        RQJobStatus.DEFERRED,
        RQJobStatus.CREATED,
    ):
        st = JobStatus.PENDING
    elif status_raw == RQJobStatus.STARTED:
        st = JobStatus.STARTED
    elif status_raw == RQJobStatus.FINISHED:
        st = JobStatus.SUCCESS
        res = job.result
    elif status_raw == RQJobStatus.FAILED:
        st = JobStatus.FAILURE
        err = str(job.exc_info) if job.exc_info else str(job.result)
    elif status_raw in (RQJobStatus.STOPPED, RQJobStatus.CANCELED):
        st = JobStatus.REVOKED
    else:
        st = JobStatus.UNKNOWN

    return JobStatusSnapshot(job_id=job_id, backend="rq", status=st, result=res, error=err)


def _status_dramatiq(
    job_id: str,
    *,
    dramatiq_queue_name: Optional[str],
    dramatiq_actor_name: Optional[str],
) -> JobStatusSnapshot:
    try:
        import dramatiq  # noqa: F401
        from dramatiq.broker import get_broker
        from dramatiq.message import Message
        from dramatiq.results import ResultMissing, Results
    except ImportError as e:  # pragma: no cover
        raise RuntimeError("dramatiq is not installed. pip install fast_jobs[dramatiq]") from e

    if not dramatiq_queue_name or not dramatiq_actor_name:
        return JobStatusSnapshot(
            job_id=job_id,
            backend="dramatiq",
            status=JobStatus.UNKNOWN,
            error="dramatiq_queue_name and dramatiq_actor_name are required",
        )

    backend = None
    try:
        broker = get_broker()
        for mw in broker.middleware:
            if isinstance(mw, Results):
                backend = mw.backend
                break
    except Exception:
        broker = None

    if backend is None:
        return JobStatusSnapshot(
            job_id=job_id,
            backend="dramatiq",
            status=JobStatus.UNKNOWN,
            error="Results middleware not found on broker; add dramatiq.results.Results",
        )

    msg = Message(
        queue_name=dramatiq_queue_name,
        actor_name=dramatiq_actor_name,
        args=(),
        kwargs={},
        options={},
        message_id=job_id,
    )

    try:
        val = backend.get_result(msg, block=False)
        return JobStatusSnapshot(
            job_id=job_id,
            backend="dramatiq",
            status=JobStatus.SUCCESS,
            result=val,
        )
    except ResultMissing:
        return JobStatusSnapshot(job_id=job_id, backend="dramatiq", status=JobStatus.PENDING)
    except Exception as exc:  # pragma: no cover - unwrap failures
        return JobStatusSnapshot(
            job_id=job_id,
            backend="dramatiq",
            status=JobStatus.FAILURE,
            error=str(exc),
        )
