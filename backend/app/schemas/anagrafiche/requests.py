"""Schemi request per il modulo Anagrafiche."""

from pydantic import BaseModel, Field, model_validator


class IndirizzoCreateRequest(BaseModel):
    """Payload per la creazione di un indirizzo."""

    tipo: str = Field(
        default="legale",
        description="Tipo indirizzo: legale, operativo, spedizione, fatturazione.",
        examples=["legale"],
    )
    is_principale: bool = Field(default=False, description="Indica l'indirizzo principale.")
    indirizzo: str | None = Field(default=None, max_length=255, examples=["Via delle Ceramiche 42"])
    citta: str | None = Field(default=None, max_length=120, examples=["Sassuolo"])
    cap: str | None = Field(default=None, max_length=10, examples=["41049"])
    provincia: str | None = Field(default=None, max_length=4, examples=["MO"])
    paese: str = Field(default="IT", max_length=2, examples=["IT"])


class IndirizzoUpdateRequest(BaseModel):
    """Payload per l'aggiornamento parziale di un indirizzo."""

    tipo: str | None = None
    is_principale: bool | None = None
    indirizzo: str | None = None
    citta: str | None = None
    cap: str | None = None
    provincia: str | None = None
    paese: str | None = None


class AnagraficaCreateRequest(BaseModel):
    """Payload per la creazione di una nuova anagrafica."""

    tipo: str = Field(
        description="Tipo soggetto: cliente, fornitore, cliente_fornitore, agente, altro.",
        examples=["cliente"],
    )
    is_persona_fisica: bool = Field(
        default=False,
        description="True per persona fisica, False per ente o società.",
    )
    ragione_sociale: str | None = Field(
        default=None,
        max_length=255,
        description="Obbligatorio se is_persona_fisica=false.",
        examples=["Edilceram S.r.l."],
    )
    cognome: str | None = Field(
        default=None,
        max_length=150,
        description="Obbligatorio se is_persona_fisica=true.",
        examples=["Ferrari"],
    )
    nome: str | None = Field(default=None, max_length=150, examples=["Marco"])
    partita_iva: str | None = Field(default=None, max_length=16, examples=["03456789012"])
    codice_fiscale: str | None = Field(default=None, max_length=20, examples=["03456789012"])
    codice_sdi: str | None = Field(
        default=None,
        max_length=7,
        description="Codice destinatario SDI (7 caratteri). Usa '0000000' se si usa la PEC.",
        examples=["M5UXCR1"],
    )
    pec: str | None = Field(default=None, max_length=255, examples=["edilceram@pec.it"])
    regime_fiscale: str | None = Field(default="RF01", max_length=10, examples=["RF01"])
    natura_giuridica: str | None = Field(default=None, max_length=50, examples=["SRL"])
    email: str | None = Field(default=None, max_length=255)
    telefono: str | None = Field(default=None, max_length=32)
    website: str | None = Field(default=None, max_length=255)
    note: str | None = None
    indirizzi: list[IndirizzoCreateRequest] = Field(
        default_factory=list,
        description="Indirizzi da associare contestualmente alla creazione.",
    )

    @model_validator(mode="after")
    def _check_nome_display(self) -> "AnagraficaCreateRequest":
        if self.is_persona_fisica and not self.cognome:
            raise ValueError("Il campo 'cognome' è obbligatorio per persona fisica.")
        if not self.is_persona_fisica and not self.ragione_sociale:
            raise ValueError("Il campo 'ragione_sociale' è obbligatorio per ente o società.")
        return self


class AnagraficaUpdateRequest(BaseModel):
    """Payload per l'aggiornamento parziale di un'anagrafica."""

    tipo: str | None = None
    is_persona_fisica: bool | None = None
    ragione_sociale: str | None = None
    cognome: str | None = None
    nome: str | None = None
    partita_iva: str | None = None
    codice_fiscale: str | None = None
    codice_sdi: str | None = None
    pec: str | None = None
    regime_fiscale: str | None = None
    natura_giuridica: str | None = None
    email: str | None = None
    telefono: str | None = None
    website: str | None = None
    note: str | None = None
    is_active: bool | None = None


class AnagraficaListParams(BaseModel):
    """Parametri di filtro per la lista anagrafiche."""

    tipo: str | None = Field(default=None, description="Filtra per tipo soggetto.")
    is_active: bool = Field(default=True, description="Filtra per stato attivo.")
    q: str | None = Field(
        default=None,
        description="Ricerca testuale su ragione sociale, cognome, P.IVA, CF.",
    )
    skip: int = Field(default=0, ge=0)
    limit: int = Field(default=50, ge=1, le=200)
