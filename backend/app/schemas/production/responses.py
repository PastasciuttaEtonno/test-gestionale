"""Schemi di risposta per mutazioni produzione demo."""

from pydantic import BaseModel, Field


class ProductionUpdateResponse(BaseModel):
    """Esito dell'aggiornamento produzione demo."""

    success: bool = Field(
        default=True,
        description="Indica se l'aggiornamento e andato a buon fine.",
        examples=[True],
    )
    tenant_id: str = Field(
        description="Tenant per cui la cache KPI e stata invalidata.",
        examples=["b91bb07d-0f6d-4fcb-90ab-2e0bcaad4c21"],
    )
    invalidated_cache_key: str = Field(
        description="Chiave Redis invalidata a seguito della mutazione.",
        examples=["tenant:b91bb07d-0f6d-4fcb-90ab-2e0bcaad4c21:dashboard:kpis"],
    )
    message: str = Field(
        default="Aggiornamento produzione registrato e cache KPI invalidata.",
        description="Messaggio descrittivo dell'operazione eseguita.",
    )
