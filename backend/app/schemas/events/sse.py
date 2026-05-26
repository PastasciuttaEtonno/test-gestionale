"""Tipi di evento SSE e struttura del messaggio."""

from typing import Any

from pydantic import BaseModel


class SseEventEnvelope(BaseModel):
    """Struttura comune di ogni evento pubblicato sul bus Redis."""

    type: str
    payload: dict[str, Any]
    tenant_id: str | None = None
    ts: str


# --- Tipi di evento ---

class EventTypes:
    """Costanti per i tipi di evento riconosciuti dal bus."""

    # Task asincroni
    TASK_PROGRESS = "task.progress"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"

    # Notifiche
    NOTIFICATION_NEW = "notification.new"

    # KPI dashboard
    KPI_UPDATED = "kpi.updated"

    # Sistema
    SYSTEM_ALERT = "system.alert"
