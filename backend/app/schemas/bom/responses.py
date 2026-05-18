"""Schemi di risposta per le distinte base."""

from datetime import datetime

from pydantic import BaseModel, Field


class BomResponse(BaseModel):
    """Rappresentazione API della distinta base."""

    id: str = Field(
        description="Identificativo univoco della distinta base.",
        examples=["c4c2b9df-cf80-4938-a1ea-369862bd6bd6"],
    )
    tenant_id: str = Field(
        description="Tenant proprietario della distinta base.",
        examples=["b91bb07d-0f6d-4fcb-90ab-2e0bcaad4c21"],
    )
    code: str = Field(
        description="Codice logico della distinta base.",
        examples=["BOM-2026-001"],
    )
    name: str = Field(
        description="Nome commerciale della distinta base.",
        examples=["Distinta Base Linea Forni"],
    )
    description: str | None = Field(
        default=None,
        description="Descrizione estesa della distinta base.",
        examples=["Componenti e semilavorati per il ciclo forno linea A."],
    )
    updated_at: datetime = Field(
        description="Timestamp ultimo aggiornamento della distinta base.",
    )
