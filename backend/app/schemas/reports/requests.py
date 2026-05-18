"""Schemi di richiesta per i report asincroni."""

from pydantic import BaseModel, Field


class GenerateReportRequest(BaseModel):
    """Payload di richiesta per l'avvio di un report asincrono."""

    tenant_id: str = Field(
        min_length=1,
        max_length=36,
        description="Identificativo del tenant per cui generare il report massivo.",
        examples=["b91bb07d-0f6d-4fcb-90ab-2e0bcaad4c21"],
    )
