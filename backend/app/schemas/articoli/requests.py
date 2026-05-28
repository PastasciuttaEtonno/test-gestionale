"""Schemi request per il modulo Articoli."""

from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

ALIQUOTE_IVA_VALIDE = {Decimal("0"), Decimal("4"), Decimal("5"), Decimal("10"), Decimal("22")}


def _valida_aliquota(value: Decimal) -> Decimal:
    """Verifica che l'aliquota IVA sia tra quelle supportate."""
    if value not in ALIQUOTE_IVA_VALIDE:
        ammesse = ", ".join(str(int(a)) for a in sorted(ALIQUOTE_IVA_VALIDE))
        raise ValueError(f"Aliquota IVA non valida. Valori ammessi: {ammesse}.")
    return value


# ── Categorie ────────────────────────────────────────────────────────────────


class CategoriaCreateRequest(BaseModel):
    """Payload per la creazione di una categoria articolo."""

    nome: str = Field(min_length=1, max_length=100, examples=["Pavimenti"])
    descrizione: str | None = Field(default=None, max_length=255)


class CategoriaUpdateRequest(BaseModel):
    """Payload per l'aggiornamento parziale di una categoria."""

    nome: str | None = Field(default=None, min_length=1, max_length=100)
    descrizione: str | None = None
    is_active: bool | None = None


# ── Articoli ───────────────────────────────────────────────────────────────


class ArticoloCreateRequest(BaseModel):
    """Payload per la creazione di un nuovo articolo."""

    codice: str = Field(min_length=1, max_length=50, examples=["PAV-GRES-6060-GR"])
    categoria_id: str | None = Field(
        default=None,
        description="Categoria dell'articolo; deve appartenere allo stesso tenant.",
    )
    descrizione: str = Field(
        min_length=1, max_length=255, examples=["Gres porcellanato 60x60 grigio"]
    )
    unita_misura: str = Field(default="pz", max_length=10, examples=["m²"])
    prezzo_unitario: Decimal = Field(default=Decimal("0"), ge=0, examples=["18.5000"])
    aliquota_iva: Decimal = Field(default=Decimal("22"), examples=["22.00"])
    giacenza: Decimal = Field(default=Decimal("0"), ge=0, examples=["420.000"])
    codice_ean: str | None = Field(default=None, max_length=14, examples=["8001234500011"])
    note: str | None = None

    @field_validator("aliquota_iva")
    @classmethod
    def _check_aliquota(cls, v: Decimal) -> Decimal:
        return _valida_aliquota(v)


class ArticoloUpdateRequest(BaseModel):
    """Payload per l'aggiornamento parziale di un articolo.

    Richiede `version` per l'optimistic locking: deve coincidere con la
    versione corrente del record, altrimenti l'aggiornamento e' rifiutato (409).
    """

    version: int = Field(description="Versione corrente attesa dell'articolo.", examples=[1])
    codice: str | None = Field(default=None, min_length=1, max_length=50)
    categoria_id: str | None = None
    descrizione: str | None = Field(default=None, min_length=1, max_length=255)
    unita_misura: str | None = Field(default=None, max_length=10)
    prezzo_unitario: Decimal | None = Field(default=None, ge=0)
    aliquota_iva: Decimal | None = None
    giacenza: Decimal | None = Field(default=None, ge=0)
    codice_ean: str | None = Field(default=None, max_length=14)
    note: str | None = None
    is_active: bool | None = None

    @field_validator("aliquota_iva")
    @classmethod
    def _check_aliquota(cls, v: Decimal | None) -> Decimal | None:
        return v if v is None else _valida_aliquota(v)


class ArticoloListParams(BaseModel):
    """Parametri di filtro per la lista articoli."""

    categoria_id: str | None = Field(default=None, description="Filtra per categoria.")
    is_active: bool = Field(default=True, description="Filtra per stato attivo.")
    q: str | None = Field(default=None, description="Ricerca testuale su codice e descrizione.")
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)
