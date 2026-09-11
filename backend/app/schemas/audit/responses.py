"""Schemi di risposta audit."""

from datetime import datetime

from pydantic import BaseModel, Field


class AuditLogResponse(BaseModel):
    """Singola voce di audit log."""

    id: str = Field(
        description="Identificativo univoco dell'evento di audit.",
        examples=["9b12c133-8f7c-441f-9bba-1cf3658b165e"],
    )
    user_id: str | None = Field(
        default=None,
        description="Utente che ha generato l'evento, quando disponibile.",
        examples=["6c4a6f77-7cc0-4709-a681-96b6cf724f83"],
    )
    username: str | None = Field(
        default=None,
        description="Username dell'utente che ha generato l'evento, quando noto.",
        examples=["tenant.admin"],
    )
    tenant_name: str | None = Field(
        default=None,
        description="Ragione sociale del tenant dell'utente, quando l'utente ne ha uno.",
        examples=["Ceramica Demo S.r.l."],
    )
    event_type: str = Field(
        description="Codice dell'evento di audit.",
        examples=["user_created"],
    )
    resource_type: str | None = Field(
        default=None,
        description="Tipo logico di risorsa associato all'evento.",
        examples=["user"],
    )
    resource_id: str | None = Field(
        default=None,
        description="Identificativo logico della risorsa associata all'evento.",
        examples=["5b15b826-d79c-4c76-8a08-04b36c077ae1"],
    )
    payload_json: dict | None = Field(
        default=None,
        description="Metadati strutturati associati all'evento.",
        examples=[{"attore": "admin", "username_creato": "audit.operatore", "ruolo": "user"}],
    )
    ip_address: str | None = Field(
        default=None,
        description="Indirizzo IP sorgente, quando rilevato.",
        examples=["127.0.0.1"],
    )
    user_agent: str | None = Field(
        default=None,
        description="User agent sorgente, quando rilevato.",
        examples=["Mozilla/5.0"],
    )
    created_at: datetime = Field(
        description="Timestamp UTC di creazione dell'evento di audit.",
        examples=["2026-05-15T09:50:56.402126Z"],
    )


class AuditLogListResponse(BaseModel):
    """Payload di elenco audit log."""

    items: list[AuditLogResponse] = Field(
        description="Collezione di eventi di audit restituita dalla query.",
    )
    total: int = Field(
        description="Numero totale di eventi di audit restituiti nella risposta corrente.",
        examples=[1],
    )
