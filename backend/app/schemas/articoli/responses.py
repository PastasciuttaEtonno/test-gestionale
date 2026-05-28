"""Schemi response per il modulo Articoli."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class CategoriaResponse(BaseModel):
    """Rappresentazione di una categoria articolo."""

    model_config = {"from_attributes": True}

    id: str
    tenant_id: str
    nome: str
    descrizione: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CategoriaListResponse(BaseModel):
    """Lista di categorie del tenant."""

    items: list[CategoriaResponse]
    total: int


class ArticoloResponse(BaseModel):
    """Rappresentazione completa di un articolo."""

    model_config = {"from_attributes": True}

    id: str
    tenant_id: str
    codice: str
    categoria_id: str | None
    descrizione: str
    unita_misura: str
    prezzo_unitario: Decimal
    aliquota_iva: Decimal
    giacenza: Decimal
    codice_ean: str | None
    note: str | None
    is_active: bool
    version: int
    created_at: datetime
    updated_at: datetime


class ArticoloListResponse(BaseModel):
    """Lista paginata di articoli."""

    items: list[ArticoloResponse]
    total: int
    skip: int
    limit: int
