"""Schemi di richiesta per la gestione utenti."""

from pydantic import BaseModel, Field, field_validator

# Allineato a NIST SP 800-63B: lunghezza minima + blacklist di valori troppo
# deboli. La complessita' forzata (maiuscole + numeri + simboli) e' stata
# rimossa dalle linee guida moderne: produce password tipo "Password1!" che
# sono tra le piu' compromesse nei breach. Meglio passphrase lunghe.
PASSWORD_MIN_LENGTH = 12
PASSWORD_BLACKLIST = frozenset(
    {
        "password",
        "passw0rd",
        "password1",
        "password123",
        "admin",
        "administrator",
        "qwerty",
        "qwerty123",
        "letmein",
        "welcome",
        "gestionale",
        "ceramica",
        "12345678",
        "123456789",
        "1234567890",
    }
)


def _valida_robustezza_password(password: str) -> str:
    """Applica le regole minime NIST 800-63B sulla password.

    Non sostituisce la verifica HIBP (eseguita lato service), ma blocca
    immediatamente i casi piu' banali senza nemmeno chiamare il servizio.
    """
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(f"La password deve avere almeno {PASSWORD_MIN_LENGTH} caratteri.")
    if password.lower() in PASSWORD_BLACKLIST:
        raise ValueError("La password e' troppo comune. Scegliere un valore meno prevedibile.")
    return password


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
        min_length=PASSWORD_MIN_LENGTH,
        max_length=255,
        description=(
            "Password iniziale assegnata all'utente. Minimo "
            f"{PASSWORD_MIN_LENGTH} caratteri, non in blacklist. "
            "La verifica anti-breach (HIBP) viene eseguita lato service."
        ),
        examples=["pizza-cane-otto-mare"],
    )

    @field_validator("password")
    @classmethod
    def _validate_password(cls, v: str) -> str:
        """Valida la robustezza della password secondo NIST 800-63B."""
        return _valida_robustezza_password(v)

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
