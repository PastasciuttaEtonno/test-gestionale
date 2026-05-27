"""Test unit del refresh token family + reuse detection."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.security.request_context import SecurityRequestContext
from app.domain.security.enums import AuditEventType
from app.models.security.refresh_token import RefreshToken
from app.models.security.user import User
from app.services.auth.auth_service import AuthService


def _make_user(user_id: str = "user-001", role_code: str = "user", active: bool = True) -> User:
    user = User(
        username="mario.rossi",
        password_hash="hash",
        role_code=role_code,
        is_active=active,
        person_id=None,
        tenant_id="tenant-001",
    )
    user.id = user_id
    return user


def _make_refresh_token(
    *,
    user_id: str = "user-001",
    jti: str | None = None,
    family_id: str | None = None,
    family_age_days: int = 0,
    revoked: bool = False,
    revoked_reason: str | None = None,
) -> RefreshToken:
    now = datetime.now(UTC)
    token = RefreshToken(
        user_id=user_id,
        token_identifier=jti or str(uuid4()),
        family_id=family_id or str(uuid4()),
        parent_token_identifier=None,
        family_created_at=now - timedelta(days=family_age_days),
        issued_at=now - timedelta(minutes=5),
        expires_at=now + timedelta(days=7),
        ip_address="127.0.0.1",
        user_agent="pytest",
    )
    if revoked:
        token.revoked_at = now - timedelta(seconds=1)
        token.revoked_reason = revoked_reason or "Rotazione refresh token."
    return token


def _make_service(
    *,
    decoded_token: dict,
    refresh_token: RefreshToken | None,
    user: User | None,
) -> AuthService:
    service = AuthService.__new__(AuthService)
    service.session = MagicMock()
    service.session.commit = MagicMock()

    service.jwt_token_manager = MagicMock()
    service.jwt_token_manager.decode_token = MagicMock(return_value=decoded_token)
    service.jwt_token_manager.create_access_token = MagicMock(return_value="access-token-nuovo")
    service.jwt_token_manager.create_refresh_token = MagicMock(
        return_value=("refresh-token-nuovo", "new-jti", datetime.now(UTC) + timedelta(days=7))
    )

    service.refresh_token_repository = MagicMock()
    service.refresh_token_repository.get_by_identifier = AsyncMock(return_value=refresh_token)
    service.refresh_token_repository.revoke = AsyncMock()
    service.refresh_token_repository.revoke_family = AsyncMock(return_value=3)
    service.refresh_token_repository.persist = AsyncMock()

    service.user_repository = MagicMock()
    service.user_repository.get_user = AsyncMock(return_value=user)

    service.role_repository = MagicMock()
    service.role_repository.list_permissions_by_role = AsyncMock(return_value=["users.read"])

    service.audit_repository = MagicMock()
    service.audit_repository.log_event = AsyncMock()
    return service


def _request_context() -> SecurityRequestContext:
    return SecurityRequestContext(ip_address="127.0.0.1", user_agent="pytest")


def _audit_events(service: AuthService) -> list[str]:
    """Estrae i tipi degli eventi audit registrati durante il test."""
    return [
        call_args.args[0].event_type
        for call_args in service.audit_repository.log_event.call_args_list
    ]


def test_refresh_legittimo_ruota_token_e_preserva_famiglia() -> None:
    """Un refresh valido ruota il token e mantiene la stessa famiglia."""
    family_id = "family-123"
    token = _make_refresh_token(jti="old-jti", family_id=family_id)
    service = _make_service(
        decoded_token={"type": "refresh", "jti": "old-jti", "sub": "user-001"},
        refresh_token=token,
        user=_make_user(),
    )

    result = asyncio.run(service.refresh("refresh-token-corrente", _request_context()))

    assert result.refresh_token == "refresh-token-nuovo"
    service.refresh_token_repository.revoke.assert_awaited_once_with(
        token_identifier="old-jti",
        revoked_reason="Rotazione refresh token.",
    )
    persisted = service.refresh_token_repository.persist.await_args.args[0]
    assert persisted.family_id == family_id
    assert persisted.parent_token_identifier == "old-jti"
    assert AuditEventType.TOKEN_REFRESH.value in _audit_events(service)


def test_riuso_di_token_revocato_revoca_intera_famiglia() -> None:
    """Riusare un refresh gia' ruotato deve revocare l'intera famiglia."""
    family_id = "family-attacco"
    token_revocato = _make_refresh_token(
        jti="rubato-jti",
        family_id=family_id,
        revoked=True,
        revoked_reason="Rotazione refresh token.",
    )
    service = _make_service(
        decoded_token={"type": "refresh", "jti": "rubato-jti", "sub": "user-001"},
        refresh_token=token_revocato,
        user=_make_user(),
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(service.refresh("refresh-token-rubato", _request_context()))

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    service.refresh_token_repository.revoke_family.assert_awaited_once()
    args = service.refresh_token_repository.revoke_family.await_args
    assert args.kwargs["family_id"] == family_id
    eventi = _audit_events(service)
    assert AuditEventType.REFRESH_REUSE_DETECTED.value in eventi
    assert AuditEventType.REFRESH_FAMILY_REVOKED.value in eventi
    service.refresh_token_repository.persist.assert_not_awaited()


def test_jti_sconosciuto_audita_reuse_e_restituisce_401() -> None:
    """Un jti firmato ma mai persistito audita REFRESH_REUSE_DETECTED e nega l'accesso."""
    service = _make_service(
        decoded_token={"type": "refresh", "jti": "jti-mai-emesso", "sub": "user-001"},
        refresh_token=None,
        user=_make_user(),
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(service.refresh("token-garbage", _request_context()))

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    eventi = _audit_events(service)
    assert AuditEventType.REFRESH_REUSE_DETECTED.value in eventi
    service.refresh_token_repository.revoke_family.assert_not_awaited()


def test_user_mismatch_audita_reuse_e_nega_accesso() -> None:
    """jti valido ma user_id del JWT diverso dall'owner del token persistito."""
    token = _make_refresh_token(user_id="user-001", jti="jti-001", family_id="family-001")
    service = _make_service(
        decoded_token={"type": "refresh", "jti": "jti-001", "sub": "user-XYZ"},
        refresh_token=token,
        user=_make_user(),
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(service.refresh("token-manipolato", _request_context()))

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    eventi = _audit_events(service)
    assert AuditEventType.REFRESH_REUSE_DETECTED.value in eventi


def test_famiglia_oltre_max_age_viene_revocata_e_richiede_relogin() -> None:
    """Una famiglia che supera refresh_token_family_max_age_days viene chiusa."""
    eta_eccessiva = settings.refresh_token_family_max_age_days + 1
    token = _make_refresh_token(jti="jti-vecchio", family_age_days=eta_eccessiva)
    service = _make_service(
        decoded_token={"type": "refresh", "jti": "jti-vecchio", "sub": "user-001"},
        refresh_token=token,
        user=_make_user(),
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(service.refresh("refresh-token-corrente", _request_context()))

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    service.refresh_token_repository.revoke_family.assert_awaited_once()
    eventi = _audit_events(service)
    assert AuditEventType.REFRESH_FAMILY_TIMEOUT.value in eventi
    service.refresh_token_repository.persist.assert_not_awaited()


def test_refresh_per_utente_inattivo_restituisce_401_senza_emettere_token() -> None:
    """Anche con refresh valido, un utente disattivato non puo' rigenerare la sessione."""
    token = _make_refresh_token(jti="jti-001")
    service = _make_service(
        decoded_token={"type": "refresh", "jti": "jti-001", "sub": "user-001"},
        refresh_token=token,
        user=_make_user(active=False),
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(service.refresh("refresh-valido", _request_context()))

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    service.refresh_token_repository.persist.assert_not_awaited()


def test_token_di_tipo_non_refresh_viene_rifiutato() -> None:
    """Un access token presentato in luogo di un refresh deve fallire pulito."""
    service = _make_service(
        decoded_token={"type": "access", "jti": "qualcosa", "sub": "user-001"},
        refresh_token=None,
        user=_make_user(),
    )

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(service.refresh("access-token-misuse", _request_context()))

    assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
    service.refresh_token_repository.get_by_identifier.assert_not_awaited()
