"""Schemi di risposta per la configurazione tenant admin."""

from datetime import datetime

from pydantic import BaseModel, Field


class CompanySettingsResponse(BaseModel):
    """Impostazioni aziendali del tenant."""

    tenant_id: str = Field(
        description="Identificativo del tenant aziendale.",
        examples=["b91bb07d-0f6d-4fcb-90ab-2e0bcaad4c21"],
    )
    company_name: str = Field(
        description="Nome commerciale dell'azienda cliente.",
        examples=["Ceramica Demo S.r.l."],
    )
    legal_name: str | None = Field(
        default=None,
        description="Ragione sociale completa dell'azienda.",
        examples=["Ceramica Demo Societa a responsabilita limitata"],
    )
    vat_number: str | None = Field(
        default=None,
        description="Partita IVA dell'azienda.",
        examples=["IT01234567890"],
    )
    tax_code: str | None = Field(
        default=None,
        description="Codice fiscale dell'azienda.",
        examples=["01234567890"],
    )
    legal_address: str | None = Field(
        default=None,
        description="Indirizzo della sede legale.",
        examples=["Via delle Industrie 15"],
    )
    city: str | None = Field(
        default=None,
        description="Comune della sede legale.",
        examples=["Sassuolo"],
    )
    postal_code: str | None = Field(
        default=None,
        description="CAP della sede legale.",
        examples=["41049"],
    )
    province: str | None = Field(
        default=None,
        description="Provincia della sede legale.",
        examples=["MO"],
    )
    country: str | None = Field(
        default=None,
        description="Paese della sede legale.",
        examples=["Italia"],
    )
    pec_email: str | None = Field(
        default=None,
        description="Email PEC dell'azienda.",
        examples=["ceramica.demo@pec.it"],
    )
    admin_email: str | None = Field(
        default=None,
        description="Email amministrativa di riferimento.",
        examples=["amministrazione@ceramicademo.it"],
    )
    phone: str | None = Field(
        default=None,
        description="Telefono principale dell'azienda.",
        examples=["0536 123456"],
    )
    logo_url: str | None = Field(
        default=None,
        description="Percorso o URL del logo aziendale.",
        examples=["/assets/tenants/ceramica-demo/logo.svg"],
    )
    updated_at: datetime = Field(
        description="Timestamp UTC dell'ultimo aggiornamento.",
        examples=["2026-05-15T15:20:00Z"],
    )


class SmtpSettingsResponse(BaseModel):
    """Configurazione SMTP del tenant."""

    tenant_id: str = Field(
        description="Identificativo del tenant aziendale.",
        examples=["b91bb07d-0f6d-4fcb-90ab-2e0bcaad4c21"],
    )
    host: str = Field(
        description="Hostname del server SMTP configurato.",
        examples=["smtp.ceramicademo.it"],
    )
    port: int = Field(
        description="Porta del server SMTP configurato.",
        examples=[587],
    )
    username: str | None = Field(
        default=None,
        description="Username SMTP configurato.",
        examples=["notifiche@ceramicademo.it"],
    )
    sender_email: str = Field(
        description="Email mittente predefinita.",
        examples=["notifiche@ceramicademo.it"],
    )
    sender_name: str | None = Field(
        default=None,
        description="Nome mittente predefinito.",
        examples=["Ceramica Demo ERP"],
    )
    use_tls: bool = Field(
        description="Indica se il trasporto usa TLS.",
        examples=[True],
    )
    password_configured: bool = Field(
        description="Indica se una password SMTP e stata salvata lato backend.",
        examples=[True],
    )
    updated_at: datetime = Field(
        description="Timestamp UTC dell'ultimo aggiornamento.",
        examples=["2026-05-15T15:20:00Z"],
    )


class DocumentSequenceResponse(BaseModel):
    """Numerazione documentale del tenant."""

    id: str = Field(
        description="Identificativo univoco della configurazione di numerazione.",
        examples=["61f8d2c1-d9dd-4fc8-a1af-6488a41c78cc"],
    )
    tenant_id: str = Field(
        description="Identificativo del tenant proprietario della numerazione.",
        examples=["b91bb07d-0f6d-4fcb-90ab-2e0bcaad4c21"],
    )
    sequence_code: str = Field(
        description="Codice logico della numerazione documentale.",
        examples=["invoice_electronic"],
    )
    name: str = Field(
        description="Nome descrittivo della numerazione.",
        examples=["Fattura Elettronica 2026"],
    )
    prefix: str | None = Field(
        default=None,
        description="Prefisso della numerazione.",
        examples=["FE"],
    )
    next_number: int = Field(
        description="Prossimo numero disponibile.",
        examples=[184],
    )
    reset_policy: str = Field(
        description="Politica di reset della numerazione.",
        examples=["annual"],
    )
    year: int | None = Field(
        default=None,
        description="Anno di riferimento della numerazione.",
        examples=[2026],
    )
    is_active: bool = Field(
        description="Indica se la numerazione e attiva.",
        examples=[True],
    )
    updated_at: datetime = Field(
        description="Timestamp UTC dell'ultimo aggiornamento.",
        examples=["2026-05-15T15:20:00Z"],
    )


class DocumentSequenceListResponse(BaseModel):
    """Elenco numerazioni documentali del tenant."""

    items: list[DocumentSequenceResponse] = Field(
        description="Collezione di numerazioni documentali del tenant.",
    )
    total: int = Field(
        description="Numero totale di numerazioni restituite.",
        examples=[3],
    )
