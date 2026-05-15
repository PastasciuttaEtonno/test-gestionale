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
