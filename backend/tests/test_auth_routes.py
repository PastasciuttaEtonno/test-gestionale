"""Test rapidi delle route auth senza dipendere da PostgreSQL reale."""

from fastapi import status

from app.api.deps.auth import get_active_user, get_auth_service
from app.schemas.auth.responses import AuthSessionResponse, CurrentUserResponse, LogoutResponse
from app.services.auth.auth_service import AuthSessionResult


def _build_current_user() -> CurrentUserResponse:
    """Restituisce un utente autenticato fittizio coerente con gli schemi."""
    return CurrentUserResponse(
        id="user-001",
        username="tenant.admin",
        role_code="tenant_admin",
        is_active=True,
        person_id=None,
        tenant_id="tenant-001",
        permissions=["users.read"],
    )


class FakeAuthService:
    """Sostituto minimale del servizio auth per i test route-level."""

    async def login(self, payload, request_context) -> AuthSessionResult:
        return AuthSessionResult(
            response=AuthSessionResponse(
                access_token="access-token-demo",
                user=_build_current_user(),
            ),
            refresh_token="refresh-token-demo",
        )

    async def refresh(self, refresh_token_value, request_context) -> AuthSessionResult:
        return AuthSessionResult(
            response=AuthSessionResponse(
                access_token="refreshed-access-token",
                user=_build_current_user(),
            ),
            refresh_token="refresh-token-rotated",
        )

    async def logout(self, current_user, request_context) -> LogoutResponse:
        return LogoutResponse(success=True)


def test_login_restituisce_sessione_cookie_refresh_e_request_id(client) -> None:
    """Il login deve restituire sessione coerente, cookie e request id."""
    client.app.dependency_overrides[get_auth_service] = lambda: FakeAuthService()

    response = client.post(
        "/api/v1/auth/login",
        json={"identifier": "tenant.admin", "password": "tenant123"},
    )

    assert response.status_code == status.HTTP_200_OK
    body = response.json()
    assert body["access_token"] == "access-token-demo"
    assert body["user"]["username"] == "tenant.admin"
    assert response.headers["x-request-id"]
    assert "esseduesoft_refresh_token=refresh-token-demo" in response.headers["set-cookie"]


def test_refresh_senza_cookie_restituisce_401(client) -> None:
    """Il refresh senza cookie deve fallire in modo neutro."""
    client.app.dependency_overrides[get_auth_service] = lambda: FakeAuthService()

    response = client.post("/api/v1/auth/refresh")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Refresh token non valido o assente."}


def test_me_restituisce_401_senza_bearer_token(client) -> None:
    """L'endpoint me deve richiedere autenticazione."""
    client.app.dependency_overrides[get_auth_service] = lambda: FakeAuthService()

    response = client.get("/api/v1/auth/me")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {"detail": "Autenticazione richiesta."}


def test_me_restituisce_profilo_quando_l_utente_e_risolto(client) -> None:
    """L'endpoint me deve esporre il profilo autenticato corrente."""
    client.app.dependency_overrides[get_active_user] = _build_current_user

    response = client.get("/api/v1/auth/me")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["tenant_id"] == "tenant-001"
    assert response.json()["role_code"] == "tenant_admin"
