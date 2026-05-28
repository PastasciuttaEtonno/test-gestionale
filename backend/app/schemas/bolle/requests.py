"""Schemi request per il modulo Bolle / DDT."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field

CAUSALI_VALIDE = {"vendita", "conto_visione", "reso", "riparazione", "omaggio"}
TRASPORTO_A_CURA_VALIDI = {"mittente", "destinatario", "vettore"}


class BollaCreateRequest(BaseModel):
    """Payload per la creazione di una bozza di bolla."""

    anagrafica_id: str = Field(description="Destinatario del DDT; deve essere del tenant.")
    data_documento: date = Field(description="Data del documento di trasporto.")
    causale_trasporto: str = Field(default="vendita", examples=["vendita"])
    aspetto_beni: str | None = Field(default=None, max_length=60, examples=["Pallet"])
    num_colli: int | None = Field(default=None, ge=0)
    peso_kg: Decimal | None = Field(default=None, ge=0)
    trasporto_a_cura: str | None = Field(default=None, examples=["destinatario"])
    vettore: str | None = Field(default=None, max_length=120)
    note: str | None = None


class BollaUpdateRequest(BaseModel):
    """Payload per l'aggiornamento della testata (solo bozza). Richiede version."""

    version: int = Field(description="Versione corrente attesa della bolla.", examples=[1])
    anagrafica_id: str | None = None
    data_documento: date | None = None
    causale_trasporto: str | None = None
    aspetto_beni: str | None = Field(default=None, max_length=60)
    num_colli: int | None = Field(default=None, ge=0)
    peso_kg: Decimal | None = Field(default=None, ge=0)
    trasporto_a_cura: str | None = None
    vettore: str | None = Field(default=None, max_length=120)
    note: str | None = None


class RigaCreateRequest(BaseModel):
    """Payload per aggiungere una riga (snapshot dall'articolo)."""

    articolo_id: str = Field(description="Articolo da inserire; deve essere del tenant.")
    quantita: Decimal = Field(gt=0, examples=["50.000"])


class RigaUpdateRequest(BaseModel):
    """Payload per aggiornare la quantita' di una riga."""

    quantita: Decimal = Field(gt=0, examples=["75.000"])


class BollaListParams(BaseModel):
    """Parametri di filtro per la lista bolle."""

    stato: str | None = Field(default=None, description="bozza | emessa | annullata")
    anagrafica_id: str | None = Field(default=None, description="Filtra per destinatario.")
    q: str | None = Field(default=None, description="Ricerca sul numero documento.")
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)
