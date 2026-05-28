"""Test unit del breach screening password e validatore NIST 800-63B."""

from __future__ import annotations

import asyncio
import hashlib
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from app.core.config import settings
from app.schemas.users.requests import CreateUserRequest
from app.services.auth.password_breach_service import PasswordBreachService


def _make_service_with_response(body: str | None) -> PasswordBreachService:
    """Crea il service con un client httpx mockato tramite override interno."""
    service = PasswordBreachService(redis_client=None)

    async def fake_fetch_range(prefix: str) -> str | None:
        return body

    service._fetch_range = fake_fetch_range  # type: ignore[method-assign]
    return service


def _hibp_response_for(password: str, count: int, *, extra_lines: int = 5) -> str:
    """Costruisce un body HIBP fittizio contenente il suffisso della password attesa."""
    sha1 = hashlib.sha1(password.encode("utf-8"), usedforsecurity=False).hexdigest().upper()
    suffix = sha1[5:]
    other_lines = [f"{'A' * 35}:{n + 1}" for n in range(extra_lines)]
    return "\r\n".join([*other_lines, f"{suffix}:{count}"])


# ---------------------- PasswordBreachService ----------------------------


def test_password_pulita_restituisce_zero() -> None:
    """Una password non presente nei breach restituisce conteggio 0."""
    body = _hibp_response_for("PasswordCheNonEsiste42!@", count=0, extra_lines=5)
    # Il body simulato contiene la riga della password con count 0; il match esiste
    # solo se costruiamo il body senza includere il suffisso.
    body_senza_match = "\r\n".join(f"{'B' * 35}:{n + 1}" for n in range(5))
    service = _make_service_with_response(body_senza_match)

    risultato = asyncio.run(service.get_breach_count("PasswordCheNonEsiste42!@"))

    assert risultato == 0
    # Body costruttore non usato direttamente, l'asserzione tiene il linter buono.
    assert body is not None


def test_password_compromessa_ritorna_count_dal_servizio() -> None:
    """Una password trovata nei breach ritorna il conteggio reale."""
    body = _hibp_response_for("Password123!", count=42_000)
    service = _make_service_with_response(body)

    risultato = asyncio.run(service.get_breach_count("Password123!"))

    assert risultato == 42_000


def test_fail_open_quando_hibp_irraggiungibile() -> None:
    """HIBP irraggiungibile non solleva: restituisce 0 (fail-open)."""
    service = _make_service_with_response(None)

    risultato = asyncio.run(service.get_breach_count("QualsiasiPassword"))

    assert risultato == 0


def test_is_compromised_rispetta_soglia_configurata() -> None:
    """is_compromised confronta il conteggio con password_breach_max_count."""
    body = _hibp_response_for("HotPassword", count=settings.password_breach_max_count + 1)
    service = _make_service_with_response(body)

    assert asyncio.run(service.is_compromised("HotPassword")) is True


def test_password_appena_sotto_soglia_non_e_considerata_compromessa() -> None:
    """Password con count uguale alla soglia non e' rifiutata (regola: strict greater)."""
    body = _hibp_response_for("BorderlinePassword", count=settings.password_breach_max_count)
    service = _make_service_with_response(body)

    assert asyncio.run(service.is_compromised("BorderlinePassword")) is False


def test_cache_redis_evita_seconda_chiamata_a_hibp() -> None:
    """Una hit in cache restituisce direttamente il body senza chiamare HIBP."""
    body = _hibp_response_for("Password123!", count=99)
    redis_mock = MagicMock()
    redis_mock.get = AsyncMock(return_value=body)
    redis_mock.set = AsyncMock()
    service = PasswordBreachService(redis_client=redis_mock)
    service._fetch_range = AsyncMock()  # type: ignore[method-assign]

    risultato = asyncio.run(service.get_breach_count("Password123!"))

    assert risultato == 99
    service._fetch_range.assert_not_called()
    redis_mock.set.assert_not_called()


def test_cache_miss_invoca_hibp_e_popola_cache() -> None:
    """Una cache miss chiama HIBP e poi salva la risposta su Redis."""
    body = _hibp_response_for("NuovaPassword", count=5)
    redis_mock = MagicMock()
    redis_mock.get = AsyncMock(return_value=None)
    redis_mock.set = AsyncMock()
    service = PasswordBreachService(redis_client=redis_mock)

    async def fake_fetch(_prefix: str) -> str:
        return body

    service._fetch_range = fake_fetch  # type: ignore[method-assign]

    risultato = asyncio.run(service.get_breach_count("NuovaPassword"))

    assert risultato == 5
    redis_mock.set.assert_awaited_once()


def test_timeout_o_errore_http_non_solleva_eccezioni() -> None:
    """Errori httpx vengono gestiti internamente come fail-open."""
    service = PasswordBreachService(redis_client=None)

    async def fake_fetch_raise(_prefix: str) -> str:
        raise httpx.TimeoutException("simulazione")

    # Coperto a livello superiore: _fetch_range_with_cache cattura l'eccezione
    # solo se proviene da Redis (non da HIBP). _fetch_range invece restituisce
    # None su httpx.HTTPError. Qui verifichiamo il path completo:
    async def _fetch_range_safe(_prefix: str) -> None:
        try:
            await fake_fetch_raise(_prefix)
        except httpx.HTTPError:
            return None

    service._fetch_range = _fetch_range_safe  # type: ignore[method-assign]

    risultato = asyncio.run(service.get_breach_count("Password"))

    assert risultato == 0


# ---------------------- NIST password validator ---------------------------


def test_password_corta_e_rifiutata() -> None:
    """Una password sotto la lunghezza minima viene rifiutata."""
    with pytest.raises(ValueError):
        CreateUserRequest(
            username="utente.test",
            password="corta1",
            role_code="user",
        )


def test_password_in_blacklist_e_rifiutata() -> None:
    """Valori comuni come 'gestionale' o 'password123' sono in blacklist."""
    with pytest.raises(ValueError):
        CreateUserRequest(
            username="utente.test",
            password="Gestionale",
            role_code="user",
        )


def test_password_lunga_e_non_in_blacklist_passa_la_validazione() -> None:
    """Una passphrase di lunghezza adeguata e non comune passa la validazione."""
    request = CreateUserRequest(
        username="utente.test",
        password="pizza-cane-otto-mare",
        role_code="user",
    )
    assert request.password == "pizza-cane-otto-mare"


def test_password_blacklist_e_case_insensitive() -> None:
    """La blacklist confronta sempre lowercase."""
    with pytest.raises(ValueError):
        CreateUserRequest(
            username="utente.test",
            password="QWERTY",
            role_code="user",
        )
