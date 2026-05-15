"""Schemi di risposta del modulo Auth."""

from pydantic import BaseModel, Field


class CurrentUserResponse(BaseModel):
    """Utente autenticato corrente."""

    id: str = Field(
        description="Identificativo univoco dell'utente autenticato.",
        examples=["6c4a6f77-7cc0-4709-a681-96b6cf724f83"],
    )
    username: str = Field(
        description="Username associato all'utente autenticato.",
        examples=["admin"],
    )
    role_code: str = Field(
        description="Codice ruolo assegnato, usato per i controlli di autorizzazione.",
        examples=["admin", "tenant_admin"],
    )
    is_active: bool = Field(
        description="Indica se l'account utente e attivo e puo accedere al sistema.",
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
    permissions: list[str] = Field(
        default_factory=list,
        description="Elenco dei codici permesso risolti per l'utente corrente.",
        examples=[["users.read", "users.write", "audit.read"]],
    )


class TokenPairResponse(BaseModel):
    """Coppia di access token e refresh token."""

    access_token: str = Field(
        description="Access token a breve durata per invocare endpoint API protetti.",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    refresh_token: str = Field(
        description="Refresh token usato per ottenere un nuovo access token.",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    token_type: str = Field(
        default="bearer",
        description="Tipo di token restituito dal flusso di autenticazione.",
        examples=["bearer"],
    )
    user: CurrentUserResponse = Field(
        description="Profilo utente autenticato restituito dopo login o refresh.",
    )


class LogoutResponse(BaseModel):
    """Risposta di logout."""

    success: bool = Field(
        description="Indica se la richiesta di logout e stata accettata con successo.",
        examples=[True],
    )
