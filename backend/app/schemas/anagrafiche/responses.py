"""Schemi response per il modulo Anagrafiche."""

from datetime import datetime

from pydantic import BaseModel, Field, computed_field


class IndirizzoResponse(BaseModel):
    """Rappresentazione di un indirizzo anagrafica."""

    model_config = {"from_attributes": True}

    id: str
    anagrafica_id: str
    tipo: str
    is_principale: bool
    indirizzo: str | None
    citta: str | None
    cap: str | None
    provincia: str | None
    paese: str
    created_at: datetime
    updated_at: datetime


class AnagraficaResponse(BaseModel):
    """Rappresentazione completa di un'anagrafica."""

    model_config = {"from_attributes": True}

    id: str
    tenant_id: str
    tipo: str
    is_persona_fisica: bool
    ragione_sociale: str | None
    cognome: str | None
    nome: str | None
    partita_iva: str | None
    codice_fiscale: str | None
    codice_sdi: str | None
    pec: str | None
    regime_fiscale: str | None
    natura_giuridica: str | None
    email: str | None
    telefono: str | None
    website: str | None
    note: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    indirizzi: list[IndirizzoResponse] = Field(default_factory=list)

    @computed_field
    @property
    def display_name(self) -> str:
        """Nome visualizzato: ragione sociale o cognome+nome."""
        if self.ragione_sociale:
            return self.ragione_sociale
        parts = [self.cognome, self.nome]
        return " ".join(p for p in parts if p) or "—"


class AnagraficaListResponse(BaseModel):
    """Lista paginata di anagrafiche."""

    items: list[AnagraficaResponse]
    total: int
    skip: int
    limit: int
