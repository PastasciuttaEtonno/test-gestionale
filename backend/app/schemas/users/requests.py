"""Schemi di richiesta per la gestione utenti."""

from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    """Payload di creazione utente."""

    username: str = Field(
        min_length=1,
        max_length=150,
        description="Username univoco per il nuovo utente applicativo.",
        examples=["warehouse.operator"],
    )
    email: str | None = Field(
        default=None,
        max_length=255,
        description="Email opzionale associata all'account utente.",
        examples=["warehouse.operator@example.local"],
    )
    password: str = Field(
        min_length=8,
        max_length=255,
        description="Password iniziale assegnata all'utente.",
        examples=["StrongPass123!"],
    )
    role_code: str = Field(
        min_length=1,
        max_length=50,
        description="Codice ruolo assegnato all'utente.",
        examples=["user", "tenant_admin"],
    )
    is_active: bool = Field(
        default=True,
        description="Indica se l'account e attivo subito dopo la creazione.",
        examples=[True],
    )
    person_id: str | None = Field(
        default=None,
        description="Collegamento opzionale futuro al profilo anagrafico canonico.",
        examples=["person-001"],
    )
    tenant_id: str | None = Field(
        default=None,
        description=(
            "Tenant aziendale da associare al nuovo utente; obbligatorio per "
            "ruoli tenant-scoped creati dal super admin."
        ),
        examples=["b91bb07d-0f6d-4fcb-90ab-2e0bcaad4c21"],
    )


class UpdateUserRequest(BaseModel):
    """Payload di aggiornamento utente."""

    email: str | None = Field(
        default=None,
        max_length=255,
        description="Email aggiornata associata all'account utente.",
        examples=["updated.user@example.local"],
    )
    person_id: str | None = Field(
        default=None,
        description="Collegamento futuro aggiornato al profilo anagrafico canonico.",
        examples=["person-002"],
    )


class ChangeUserStatusRequest(BaseModel):
    """Payload di modifica stato."""

    is_active: bool = Field(
        description="Stato di attivazione desiderato per l'account utente.",
        examples=[False],
    )


class ChangeUserRoleRequest(BaseModel):
    """Payload di modifica ruolo."""

    role_code: str = Field(
        min_length=1,
        max_length=50,
        description="Nuovo codice ruolo assegnato all'utente.",
        examples=["admin", "tenant_admin"],
    )
