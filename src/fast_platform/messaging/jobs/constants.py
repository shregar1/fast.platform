from typing import Final

CELERY_BACKEND: Final[str] = "celery"
RQ_BACKEND: Final[str] = "rq"
DRAMATIQ_BACKEND: Final[str] = "dramatiq"
CELERY_INSTALL_ERROR: Final[str] = "celery is not installed. pip install fast_jobs[celery]"
