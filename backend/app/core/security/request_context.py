"""Contesto di sicurezza derivato dalla richiesta HTTP."""

from dataclasses import dataclass

from fastapi import Request


@dataclass(slots=True)
class SecurityRequestContext:
    """Metadati utili ai flussi di sicurezza e audit."""

    ip_address: str | None
    user_agent: str | None


def build_security_request_context(request: Request) -> SecurityRequestContext:
    """Estrae IP e user-agent dalla richiesta corrente."""
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        ip_address = forwarded_for.split(",")[0].strip()
    else:
        ip_address = request.client.host if request.client is not None else None

    user_agent = request.headers.get("user-agent")
    return SecurityRequestContext(ip_address=ip_address, user_agent=user_agent)
