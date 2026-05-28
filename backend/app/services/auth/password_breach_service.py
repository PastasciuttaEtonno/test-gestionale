"""Servizio di verifica password contro la lista HIBP Pwned Passwords.

Usa il modello k-anonymity (RFC nessuna, ma pattern industria): inviamo solo
i primi 5 caratteri esadecimali dello SHA1 della password al servizio HIBP,
che restituisce tutti i suffissi sotto quel prefisso (circa 600-900 righe).
Cerchiamo il match localmente. HIBP non puo' ricostruire la password.
"""

from __future__ import annotations

import hashlib
import logging

import httpx
from redis.asyncio import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)

HIBP_RANGE_ENDPOINT = "https://api.pwnedpasswords.com/range/{prefix}"
CACHE_KEY_PREFIX = "pwned:"


class PasswordBreachCheckUnavailable(Exception):
    """Sollevata quando HIBP e' irraggiungibile e la policy e' fail-closed."""


class PasswordBreachService:
    """Verifica password contro HIBP Pwned Passwords con k-anonymity."""

    def __init__(self, redis_client: Redis | None = None) -> None:
        self.redis_client = redis_client

    async def get_breach_count(self, password: str) -> int:
        """Restituisce quante volte la password e' apparsa nei breach noti.

        Ritorna ``0`` se la password non risulta compromessa o se la verifica
        non e' disponibile (fail-open). Il chiamante puo' interpretare il
        risultato secondo la propria policy (es. soglia configurabile).
        """
        sha1 = hashlib.sha1(password.encode("utf-8"), usedforsecurity=False).hexdigest().upper()
        prefix, suffix = sha1[:5], sha1[5:]

        body = await self._fetch_range_with_cache(prefix)
        if body is None:
            return 0

        for line in body.splitlines():
            parts = line.strip().split(":")
            if len(parts) != 2:
                continue
            hash_suffix, count_str = parts
            if hash_suffix.upper() == suffix:
                try:
                    return int(count_str)
                except ValueError:
                    return 0
        return 0

    async def is_compromised(self, password: str) -> bool:
        """True se la password supera la soglia ``password_breach_max_count``."""
        count = await self.get_breach_count(password)
        return count > settings.password_breach_max_count

    async def _fetch_range_with_cache(self, prefix: str) -> str | None:
        """Recupera la lista di suffissi per il prefisso, con cache Redis opzionale."""
        cache_key = f"{CACHE_KEY_PREFIX}{prefix}"

        if self.redis_client is not None:
            try:
                cached = await self.redis_client.get(cache_key)
                if cached:
                    return cached
            except Exception:
                logger.warning("Lettura cache breach screening fallita per il prefisso %s.", prefix)

        body = await self._fetch_range(prefix)
        if body is None:
            return None

        if self.redis_client is not None:
            try:
                await self.redis_client.set(
                    cache_key,
                    body,
                    ex=settings.password_breach_cache_ttl_seconds,
                )
            except Exception:
                logger.warning(
                    "Scrittura cache breach screening fallita per il prefisso %s.", prefix
                )
        return body

    async def _fetch_range(self, prefix: str) -> str | None:
        """Esegue la GET su HIBP. Ritorna ``None`` se irraggiungibile (fail-open)."""
        url = HIBP_RANGE_ENDPOINT.format(prefix=prefix)
        try:
            async with httpx.AsyncClient(
                timeout=settings.password_breach_api_timeout_seconds,
            ) as client:
                response = await client.get(url, headers={"Add-Padding": "true"})
                response.raise_for_status()
                return response.text
        except (httpx.HTTPError, httpx.TimeoutException) as exc:
            logger.warning("HIBP irraggiungibile per il prefisso %s: %s.", prefix, exc)
            return None
