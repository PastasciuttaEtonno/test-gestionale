"""Task Celery per lavorazioni report lunghe."""

from time import sleep

from celery import states
from sqlalchemy import select

from app.core.celery_app import celery_app
from app.core.db import get_db_session_context
from app.models.security.tenant import Tenant


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
    try:
        self.update_state(
            state="STARTED",
            meta={
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
            self.update_state(
                state="PROGRESS",
                meta={
                    "progress": 15 + (step * 15),
                    "message": f"In elaborazione batch {step}/5 per tenant {tenant_id}.",
                },
            )

        result_url = f"/downloads/reports/{tenant_id}/{self.request.id}.pdf"
        return {
            "progress": 100,
            "message": f"Report completato per tenant {tenant_id}.",
            "result_url": result_url,
            "requested_by_user_id": requested_by_user_id,
        }
    except Exception as exc:
        self.update_state(
            state=states.FAILURE,
            meta={
                "progress": 100,
                "message": "Generazione report fallita.",
            },
        )
        raise exc
