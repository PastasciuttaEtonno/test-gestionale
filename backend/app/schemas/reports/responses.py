"""Schemi di risposta per i report asincroni."""

from pydantic import BaseModel, Field


class GenerateReportAcceptedResponse(BaseModel):
    """Risposta immediata all'accodamento di un report."""

    task_id: str = Field(
        description="Identificativo univoco del task Celery accodato.",
        examples=["4f2ce2a3-52ec-4582-80ca-b95c2e2eb89c"],
    )
    status: str = Field(
        default="accepted",
        description="Stato immediato della richiesta di generazione report.",
        examples=["accepted"],
    )
    message: str = Field(
        default="Task accodato con successo.",
        description="Messaggio descrittivo restituito al chiamante.",
    )
