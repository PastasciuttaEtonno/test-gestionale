"""Schemi di risposta per i costi finance."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class FinanceCostResponse(BaseModel):
    """Rappresentazione API di un costo aziendale creato."""

    id: str = Field(
        description="Identificativo univoco del costo registrato.",
        examples=["d978f0f2-5906-4777-9e6d-965f2a0b2de1"],
    )
    tenant_id: str = Field(
        description="Tenant proprietario del costo.",
        examples=["b91bb07d-0f6d-4fcb-90ab-2e0bcaad4c21"],
    )
    cost_center: str = Field(
        description="Centro di costo di imputazione.",
        examples=["produzione-energia"],
    )
    amount: Decimal = Field(
        description="Importo del costo registrato.",
        examples=[1280.50],
    )
    currency: str = Field(
        description="Valuta del costo registrato.",
        examples=["EUR"],
    )
    note: str | None = Field(
        default=None,
        description="Nota descrittiva opzionale.",
    )
    created_at: datetime = Field(
        description="Timestamp di creazione del record di costo.",
    )
