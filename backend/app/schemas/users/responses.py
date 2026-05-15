"""Schemi di risposta per la gestione utenti."""

from pydantic import BaseModel, Field


class UserResponse(BaseModel):
    """Payload di risposta utente."""

    id: str = Field(
        description="Identificativo univoco dell'utente.",
        examples=["dba4434d-99d2-4fbb-97df-a6e46e6cd6ef"],
    )
    username: str = Field(
        description="Username dell'utente.",
        examples=["user"],
    )
    email: str | None = Field(
        default=None,
        description="Email associata all'account utente.",
        examples=["user@example.local"],
    )
    role_code: str = Field(
        description="Codice ruolo assegnato all'utente.",
        examples=["user", "tenant_admin"],
    )
    is_active: bool = Field(
        description="Indica se l'account utente e attivo.",
        examples=[True],
    )
    person_id: str | None = Field(
        default=None,
        description="Collegamento futuro al profilo anagrafico canonico.",
        examples=["person-001"],
    )
    tenant_id: str | None = Field(
        default=None,
        description="Identificativo del tenant aziendale a cui appartiene l'utente.",
        examples=["b91bb07d-0f6d-4fcb-90ab-2e0bcaad4c21"],
    )


class UserListResponse(BaseModel):
    """Elenco utenti."""

    items: list[UserResponse] = Field(
        description="Collezione di utenti restituita dalla query.",
    )
    total: int = Field(
        description="Numero totale di utenti restituiti nella risposta corrente.",
        examples=[2],
    )
