"""Schemi di richiesta per mutazioni produzione demo."""

from pydantic import BaseModel, Field


class ProductionUpdateRequest(BaseModel):
    """Payload di esempio per l'aggiornamento di uno stato produzione."""

    tenant_id: str = Field(
        min_length=1,
        max_length=36,
        description="Tenant a cui appartiene l'ordine di produzione aggiornato.",
        examples=["b91bb07d-0f6d-4fcb-90ab-2e0bcaad4c21"],
    )
    order_code: str = Field(
        min_length=1,
        max_length=100,
        description="Codice logico dell'ordine di produzione.",
        examples=["OP-2026-0042"],
    )
    status: str = Field(
        min_length=1,
        max_length=64,
        description="Nuovo stato applicato all'ordine di produzione.",
        examples=["in_lavorazione", "completato"],
    )
