"""Verifica di origin e referer per endpoint sensibili cookie-based."""

from urllib.parse import urlsplit

from fastapi import HTTPException, Request, status

from app.core.config import settings


def _estrai_origine_da_referer(referer: str) -> str | None:
    """Converte un referer completo nella sua origin canonica."""
    parsed = urlsplit(referer)
    if not parsed.scheme or not parsed.netloc:
        return None
    return f"{parsed.scheme}://{parsed.netloc}"


def require_allowed_auth_origin(request: Request) -> None:
    """Verifica che una richiesta auth sensibile provenga da una origin consentita."""
    if not settings.auth_enforce_origin_check:
        return

    allowed_origins = set(settings.effective_auth_allowed_origins)
    origin = request.headers.get("origin")
    referer = request.headers.get("referer")

    if origin and origin in allowed_origins:
        return

    referer_origin = _estrai_origine_da_referer(referer) if referer else None
    if referer_origin and referer_origin in allowed_origins:
        return

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Origine della richiesta non consentita.",
    )
