"""Schemi di richiesta per i costi aziendali."""

from decimal import Decimal

from pydantic import BaseModel, Field


class CreateFinanceCostRequest(BaseModel):
    """Payload di creazione di un costo aziendale tenant-aware."""

    tenant_id: str = Field(
        min_length=1,
        max_length=36,
        description="Tenant a cui appartiene il costo aziendale.",
        examples=["b91bb07d-0f6d-4fcb-90ab-2e0bcaad4c21"],
    )
    cost_center: str = Field(
        min_length=1,
        max_length=100,
        description="Centro di costo o categoria di imputazione.",
        examples=["produzione-energia"],
    )
    amount: Decimal = Field(
        gt=0,
        description="Importo monetario del costo registrato.",
        examples=[1280.50],
    )
    currency: str = Field(
        default="EUR",
        min_length=3,
        max_length=3,
        description="Codice valuta ISO del costo.",
        examples=["EUR"],
    )
    note: str | None = Field(
        default=None,
        max_length=1000,
        description="Nota descrittiva opzionale del costo inserito.",
        examples=["Consuntivo energia reparto smalteria maggio 2026."],
    )
