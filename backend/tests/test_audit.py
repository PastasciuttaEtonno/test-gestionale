"""Test unit dell'AuditService: autore dell'evento e oscuramento nella demo pubblica."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.config import settings
from app.models.security.audit_log import AuditLog
from app.services.audit.audit_service import AuditService

TENANT_A = "11111111-1111-4111-8111-111111111111"


def _evento(event_type: str = "login_success", payload: dict | None = None) -> AuditLog:
    evento = AuditLog(
        event_type=event_type,
        user_id="user-1",
        payload_json=payload if payload is not None else {"username": "tenant.admin"},
        ip_address="203.0.113.7",
        user_agent="Mozilla/5.0",
    )
    evento.id = "evento-1"
    evento.created_at = datetime.now(UTC)
    return evento


def _make_service(rows: list) -> AuditService:
    service = AuditService(MagicMock())
    service.audit_repository = MagicMock()
    service.audit_repository.list_events = AsyncMock(return_value=rows)
    service.audit_repository.list_events_by_tenant = AsyncMock(return_value=rows)
    return service


def test_ogni_evento_porta_username_e_tenant_dell_autore(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "demo_readonly", False)
    service = _make_service([(_evento(), "tenant.admin", "Ceramica Demo S.r.l.")])

    result = asyncio.run(service.list_events(limit=50))

    service.audit_repository.list_events.assert_awaited_once_with(50)
    evento = result.items[0]
    assert evento.username == "tenant.admin"
    assert evento.tenant_name == "Ceramica Demo S.r.l."
    assert evento.ip_address == "203.0.113.7"
    assert result.total == 1


def test_audit_del_tenant_passa_tenant_e_limite_al_repository(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "demo_readonly", False)
    service = _make_service([])

    asyncio.run(service.list_events_for_tenant(TENANT_A, limit=20))

    service.audit_repository.list_events_by_tenant.assert_awaited_once_with(TENANT_A, 20)


def test_in_demo_ip_e_user_agent_sono_oscurati(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "demo_readonly", True)
    service = _make_service([(_evento(), "tenant.admin", "Ceramica Demo S.r.l.")])

    evento = asyncio.run(service.list_events()).items[0]

    assert evento.ip_address is None
    assert evento.user_agent is None
    assert evento.username == "tenant.admin"


def test_in_demo_l_identificativo_digitato_al_login_e_oscurato(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "demo_readonly", True)
    payload = {"identificativo": "mario.rossi@example.com", "tentativi_falliti": 2}
    service = _make_service([(_evento("login_failed", payload), None, None)])

    evento = asyncio.run(service.list_events()).items[0]

    assert evento.payload_json == {"tentativi_falliti": 2}
