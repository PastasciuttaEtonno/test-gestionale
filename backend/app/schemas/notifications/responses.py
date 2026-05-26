"""Schemi di risposta per le notifiche applicative."""

from datetime import datetime

from pydantic import BaseModel, Field


class NotificationResponse(BaseModel):
    """Singola notifica serializzata per il frontend."""

    id: str
    event_type: str
    title: str
    body: str
    payload: str | None = None
    is_read: bool
    read_at: datetime | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationListResponse(BaseModel):
    """Lista paginata di notifiche con conteggio non lette."""

    items: list[NotificationResponse] = Field(default_factory=list)
    unread_count: int = Field(ge=0)
    total: int = Field(ge=0)


class MarkReadResponse(BaseModel):
    """Risposta alla marcatura di notifiche come lette."""

    updated: int = Field(ge=0, description="Numero di notifiche aggiornate.")
