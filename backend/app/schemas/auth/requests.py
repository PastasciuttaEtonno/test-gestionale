"""Schemi di richiesta del modulo Auth."""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Payload di login."""

    identifier: str = Field(
        min_length=1,
        max_length=255,
        description="Identificativo principale di login. In questa fase coincide con lo username.",
        examples=["admin"],
    )
    password: str = Field(
        min_length=1,
        max_length=255,
        description="Password in chiaro inviata durante il login.",
        examples=["admin123"],
    )


class RefreshTokenRequest(BaseModel):
    """Payload del refresh token."""

    refresh_token: str = Field(
        min_length=1,
        description="Refresh token associato alla sessione autenticata corrente.",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
