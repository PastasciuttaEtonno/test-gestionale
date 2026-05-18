"""Schemi di risposta per lo stato dei task."""

from pydantic import BaseModel, Field


class TaskStatusResponse(BaseModel):
    """Stato sintetico di un task asincrono."""

    task_id: str = Field(
        description="Identificativo univoco del task asincrono.",
        examples=["4f2ce2a3-52ec-4582-80ca-b95c2e2eb89c"],
    )
    status: str = Field(
        description="Stato corrente del task Celery.",
        examples=["pending", "started", "progress", "success", "failure"],
    )
    progress: int = Field(
        default=0,
        ge=0,
        le=100,
        description="Percentuale di avanzamento logico del task.",
        examples=[0, 40, 100],
    )
    message: str = Field(
        description="Messaggio descrittivo dello stato corrente del task.",
        examples=["Task in coda.", "In elaborazione batch 2/5.", "Completato."],
    )
    result_url: str | None = Field(
        default=None,
        description="URL logico del file generato, quando disponibile.",
        examples=["/downloads/reports/tenant-001/task-001.pdf"],
    )
