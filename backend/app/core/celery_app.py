"""Bootstrap separato dell'app Celery."""

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "esseduesoft-core-worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend_url,
)

celery_app.conf.update(
    task_default_queue=settings.celery_task_default_queue,
    task_track_started=settings.celery_task_track_started,
    broker_connection_retry_on_startup=True,
    result_expires=3600,
    timezone="UTC",
    enable_utc=True,
    imports=("app.tasks.report_tasks",),
)
