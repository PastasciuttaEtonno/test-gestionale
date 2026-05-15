"""Schemi di richiesta per la configurazione tenant admin."""

from pydantic import BaseModel, Field


class UpdateCompanySettingsRequest(BaseModel):
    """Payload di aggiornamento impostazioni aziendali."""

    company_name: str = Field(
        min_length=1,
        max_length=255,
        description="Nome commerciale dell'azienda cliente.",
        examples=["Ceramica Demo S.r.l."],
    )
    legal_name: str | None = Field(
        default=None,
        max_length=255,
        description="Ragione sociale completa dell'azienda.",
        examples=["Ceramica Demo Societa a responsabilita limitata"],
    )
    vat_number: str | None = Field(
        default=None,
        max_length=32,
        description="Partita IVA dell'azienda.",
        examples=["IT01234567890"],
    )
    tax_code: str | None = Field(
        default=None,
        max_length=32,
        description="Codice fiscale dell'azienda, se distinto dalla partita IVA.",
        examples=["01234567890"],
    )
    legal_address: str | None = Field(
        default=None,
        max_length=255,
        description="Indirizzo della sede legale.",
        examples=["Via delle Industrie 15"],
    )
    city: str | None = Field(
        default=None,
        max_length=120,
        description="Comune della sede legale.",
        examples=["Sassuolo"],
    )
    postal_code: str | None = Field(
        default=None,
        max_length=16,
        description="CAP della sede legale.",
        examples=["41049"],
    )
    province: str | None = Field(
        default=None,
        max_length=8,
        description="Provincia della sede legale.",
        examples=["MO"],
    )
    country: str | None = Field(
        default=None,
        max_length=120,
        description="Paese della sede legale.",
        examples=["Italia"],
    )
    pec_email: str | None = Field(
        default=None,
        max_length=255,
        description="Indirizzo PEC dell'azienda.",
        examples=["ceramica.demo@pec.it"],
    )
    admin_email: str | None = Field(
        default=None,
        max_length=255,
        description="Email amministrativa di riferimento.",
        examples=["amministrazione@ceramicademo.it"],
    )
    phone: str | None = Field(
        default=None,
        max_length=32,
        description="Numero di telefono principale.",
        examples=["0536 123456"],
    )
    logo_url: str | None = Field(
        default=None,
        max_length=512,
        description="Percorso o URL del logo aziendale usato nei documenti.",
        examples=["/assets/tenants/ceramica-demo/logo.svg"],
    )


class UpdateSmtpSettingsRequest(BaseModel):
    """Payload di aggiornamento configurazione SMTP tenant."""

    host: str = Field(
        min_length=1,
        max_length=255,
        description="Hostname del server SMTP aziendale.",
        examples=["smtp.ceramicademo.it"],
    )
    port: int = Field(
        ge=1,
        le=65535,
        description="Porta del server SMTP aziendale.",
        examples=[587],
    )
    username: str | None = Field(
        default=None,
        max_length=255,
        description="Username usato per l'autenticazione SMTP.",
        examples=["notifiche@ceramicademo.it"],
    )
    password: str | None = Field(
        default=None,
        min_length=8,
        max_length=255,
        description=(
            "Password SMTP in chiaro fornita dal tenant admin; viene cifrata lato "
            "backend e non viene mai restituita in risposta."
        ),
        examples=["TenantSmtp123!"],
    )
    sender_email: str = Field(
        min_length=1,
        max_length=255,
        description="Email mittente predefinita.",
        examples=["notifiche@ceramicademo.it"],
    )
    sender_name: str | None = Field(
        default=None,
        max_length=255,
        description="Nome mittente predefinito visualizzato nelle email.",
        examples=["Ceramica Demo ERP"],
    )
    use_tls: bool = Field(
        default=True,
        description="Indica se il trasporto SMTP usa TLS.",
        examples=[True],
    )


class UpdateDocumentSequenceRequest(BaseModel):
    """Payload di aggiornamento numerazione documentale del tenant."""

    name: str = Field(
        min_length=1,
        max_length=255,
        description="Nome descrittivo della numerazione documentale.",
        examples=["Fattura Elettronica 2026"],
    )
    prefix: str | None = Field(
        default=None,
        max_length=32,
        description="Prefisso della numerazione.",
        examples=["FE"],
    )
    next_number: int = Field(
        ge=1,
        description="Prossimo numero che verra usato per il documento.",
        examples=[184],
    )
    reset_policy: str = Field(
        min_length=1,
        max_length=32,
        description="Politica di reset della numerazione.",
        examples=["annual"],
    )
    year: int | None = Field(
        default=None,
        ge=2000,
        le=2100,
        description="Anno di riferimento della numerazione, se applicabile.",
        examples=[2026],
    )
    is_active: bool = Field(
        default=True,
        description="Indica se la numerazione e utilizzabile.",
        examples=[True],
    )
