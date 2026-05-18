"""Test unitari della dependency RBAC tenant-aware."""

import asyncio

import pytest
from fastapi import HTTPException, status
from starlette.requests import Request

from app.api.deps.rbac import RequirePermission
from app.schemas.auth.responses import CurrentUserResponse


def _build_request(
    *,
    method: str = "GET",
    path: str = "/test",
    query_string: bytes = b"",
    path_params: dict[str, str] | None = None,
) -> Request:
    """Costruisce una Request minimale per i test unitari della dependency."""
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "headers": [],
        "query_string": query_string,
        "path_params": path_params or {},
    }
    return Request(scope)


def _build_user(*, tenant_id: str | None = "tenant-001") -> CurrentUserResponse:
    """Restituisce un utente autenticato fittizio per i test RBAC."""
    return CurrentUserResponse(
        id="user-001",
        username="worker.demo",
        role_code="worker",
        is_active=True,
        person_id=None,
        tenant_id=tenant_id,
        permissions=["production.write", "dashboard.read"],
    )


def test_require_permission_consentita_stesso_tenant() -> None:
    """La dependency deve accettare accesso quando tenant e permesso coincidono."""
    dependency = RequirePermission("dashboard", "read", tenant_field_name="tenant_id")
    request = _build_request(query_string=b"tenant_id=tenant-001")

    result = asyncio.run(dependency(request=request, current_user=_build_user(), session=None))

    assert result.username == "worker.demo"


def test_require_permission_blocca_tenant_mismatch() -> None:
    """La dependency deve negare accesso cross-tenant."""
    dependency = RequirePermission("dashboard", "read", tenant_field_name="tenant_id")
    request = _build_request(query_string=b"tenant_id=tenant-002")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(dependency(request=request, current_user=_build_user(), session=None))

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "Risorsa non accessibile per il tenant corrente."


def test_require_permission_blocca_permesso_mancante() -> None:
    """La dependency deve negare accesso se manca il permesso richiesto."""
    dependency = RequirePermission("finance.costs", "write", tenant_field_name="tenant_id")
    request = _build_request(query_string=b"tenant_id=tenant-001")

    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(dependency(request=request, current_user=_build_user(), session=None))

    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc_info.value.detail == "Permesso negato."
