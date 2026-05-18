"""Contesto di sicurezza derivato dalla richiesta HTTP."""

from dataclasses import dataclass

from fastapi import Request

from app.core.config import settings


@dataclass(slots=True)
class SecurityRequestContext:
    """Metadati utili ai flussi di sicurezza e audit."""

    ip_address: str | None
    user_agent: str | None


def build_security_request_context(request: Request) -> SecurityRequestContext:
    """Estrae IP e user-agent dalla richiesta corrente."""
    client_host = request.client.host if request.client is not None else None
    forwarded_for = request.headers.get("x-forwarded-for")
    trusted_proxy_ips = set(settings.trusted_proxy_ips)

    if client_host in trusted_proxy_ips and forwarded_for:
        ip_address = forwarded_for.split(",")[0].strip()
    else:
        ip_address = client_host

    user_agent = request.headers.get("user-agent")
    return SecurityRequestContext(ip_address=ip_address, user_agent=user_agent)
