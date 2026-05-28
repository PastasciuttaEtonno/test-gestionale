"""Schemi response per il modulo Bolle / DDT."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel


class RigaResponse(BaseModel):
    """Riga di una bolla (snapshot dei dati articolo)."""

    model_config = {"from_attributes": True}

    id: str
    articolo_id: str | None
    codice_articolo: str | None
    descrizione: str
    unita_misura: str
    quantita: Decimal
    prezzo_unitario: Decimal
    aliquota_iva: Decimal
    importo_riga: Decimal
    ordine: int


class BollaResponse(BaseModel):
    """Rappresentazione completa di una bolla con righe."""

    model_config = {"from_attributes": True}

    id: str
    tenant_id: str
    numero: str | None
    anno: int | None
    stato: str
    data_documento: date
    anagrafica_id: str
    causale_trasporto: str
    aspetto_beni: str | None
    num_colli: int | None
    peso_kg: Decimal | None
    trasporto_a_cura: str | None
    vettore: str | None
    note: str | None
    totale_imponibile: Decimal
    totale_iva: Decimal
    totale: Decimal
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime
    righe: list[RigaResponse] = []


class BollaListItem(BaseModel):
    """Riga sintetica per l'elenco bolle (senza dettaglio righe)."""

    model_config = {"from_attributes": True}

    id: str
    numero: str | None
    stato: str
    data_documento: date
    anagrafica_id: str
    totale: Decimal
    created_at: datetime


class BollaListResponse(BaseModel):
    """Lista paginata di bolle."""

    items: list[BollaListItem]
    total: int
    skip: int
    limit: int
