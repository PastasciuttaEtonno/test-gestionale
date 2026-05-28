"""Schemi di risposta per la dashboard tenant-aware."""

from datetime import datetime

from pydantic import BaseModel, Field


class DashboardKpisResponse(BaseModel):
    """Snapshot KPI della dashboard di un tenant."""

    tenant_id: str = Field(
        description="Identificativo del tenant a cui appartiene il cruscotto.",
        examples=["b91bb07d-0f6d-4fcb-90ab-2e0bcaad4c21"],
    )
    total_users: int = Field(
        description="Numero totale di utenti associati al tenant.",
        examples=[24],
    )
    active_users: int = Field(
        description="Numero di utenti attivi associati al tenant.",
        examples=[19],
    )
    audit_events_last_24h: int = Field(
        description="Numero di eventi audit tenant-aware registrati nelle ultime 24 ore.",
        examples=[84],
    )
    total_articoli: int = Field(
        default=0,
        description="Numero di articoli attivi a catalogo per il tenant.",
        examples=[128],
    )
    company_profile_configured: bool = Field(
        description="Indica se il tenant ha gia configurato l'anagrafica aziendale.",
        examples=[True],
    )
    smtp_configured: bool = Field(
        description="Indica se il tenant ha gia configurato il canale SMTP.",
        examples=[True],
    )
    generated_at: datetime = Field(
        description="Timestamp UTC di generazione dello snapshot KPI.",
    )
