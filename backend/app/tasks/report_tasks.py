"""Task Celery per lavorazioni report lunghe."""

from time import sleep

from celery import states
from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.db import get_db_session_context
from app.models.security.tenant import Tenant
from app.schemas.events.sse import EventTypes
from app.services.events.sync_publisher import SyncEventPublisher


@celery_app.task(
    bind=True,
    name="app.tasks.report_tasks.genera_report_massivo_task",
)
def genera_report_massivo_task(
    self,
    tenant_id: str,
    requested_by_user_id: str,
) -> dict[str, str | int]:
    """Simula un report massivo usando una sessione DB propria del worker."""
    task_id = self.request.id

    with SyncEventPublisher() as publisher:
        try:
            self.update_state(
                state="STARTED",
                meta={"progress": 5, "message": "Validazione tenant e inizializzazione report."},
            )
            publisher.publish_to_tenant(
                tenant_id,
                EventTypes.TASK_PROGRESS,
                {
                    "task_id": task_id,
                    "progress": 5,
                    "message": "Validazione tenant e inizializzazione report.",
                },
            )

            with get_db_session_context() as session:
                tenant = session.scalar(select(Tenant).where(Tenant.id == tenant_id))
                if tenant is None:
                    raise ValueError("Tenant non trovato.")

            for step in range(1, 6):
                sleep(2)
                progress = 15 + (step * 15)
                message = f"In elaborazione batch {step}/5 per tenant {tenant_id}."
                self.update_state(
                    state="PROGRESS",
                    meta={"progress": progress, "message": message},
                )
                publisher.publish_to_tenant(
                    tenant_id,
                    EventTypes.TASK_PROGRESS,
                    {"task_id": task_id, "progress": progress, "message": message},
                )

            result_url = f"/downloads/reports/{tenant_id}/{task_id}.pdf"
            final_message = f"Report completato per tenant {tenant_id}."
            publisher.publish_to_tenant(
                tenant_id,
                EventTypes.TASK_COMPLETED,
                {
                    "task_id": task_id,
                    "progress": 100,
                    "message": final_message,
                    "result_url": result_url,
                },
            )
            return {
                "progress": 100,
                "message": final_message,
                "result_url": result_url,
                "requested_by_user_id": requested_by_user_id,
            }

        except Exception as exc:
            self.update_state(
                state=states.FAILURE,
                meta={"progress": 100, "message": "Generazione report fallita."},
            )
            publisher.publish_to_tenant(
                tenant_id,
                EventTypes.TASK_FAILED,
                {"task_id": task_id, "message": str(exc)},
            )
            raise exc
