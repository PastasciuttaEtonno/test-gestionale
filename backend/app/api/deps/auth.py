"""Dependency di autenticazione e autorizzazione.

Le dependency di ruolo (require_admin, require_tenant_admin, require_admin_or_tenant_admin)
sono destinate a risorse identity/security (Users, Tenants, Audit) dove l'admin necessita
di visibilità cross-tenant. Per risorse di dominio (Anagrafiche, BOM, Finance…) usare
RequirePermission in deps/rbac.py — vedi quel modulo per la regola decisionale completa.
"""

from fastapi import Depends, HTTPException, Query, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.db import get_db_session
from app.domain.security.constants import ADMIN_ROLE, TENANT_ADMIN_ROLE
from app.domain.security.exceptions import InactiveUserError, InvalidTokenError
from app.schemas.auth.responses import CurrentUserResponse
from app.services.auth.auth_service import AuthService

bearer_scheme = HTTPBearer(auto_error=False)


def get_auth_service(session: Session = Depends(get_db_session)) -> AuthService:
    """Restituisce la dependency del servizio di autenticazione."""
    return AuthService(session)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> CurrentUserResponse:
    """Risolve l'utente corrente a partire dal token di accesso."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticazione richiesta.",
        )

    try:
        return await auth_service.get_current_user(credentials.credentials)
    except (InvalidTokenError, InactiveUserError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc


async def get_optional_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> CurrentUserResponse | None:
    """Risolve l'utente corrente quando disponibile, altrimenti restituisce None."""
    if credentials is None:
        return None

    try:
        return await auth_service.get_current_user(credentials.credentials)
    except (InvalidTokenError, InactiveUserError):
        return None


async def get_active_user(
    current_user: CurrentUserResponse = Depends(get_current_user),
) -> CurrentUserResponse:
    """Verifica che l'utente corrente sia attivo."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utente non attivo.",
        )
    return current_user


async def require_admin(
    current_user: CurrentUserResponse = Depends(get_active_user),
) -> CurrentUserResponse:
    """Verifica che l'utente corrente abbia ruolo amministratore."""
    if current_user.role_code != ADMIN_ROLE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ruolo admin richiesto.",
        )
    return current_user


async def require_tenant_admin(
    current_user: CurrentUserResponse = Depends(get_active_user),
) -> CurrentUserResponse:
    """Verifica che l'utente corrente abbia ruolo tenant admin."""
    if current_user.role_code != TENANT_ADMIN_ROLE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ruolo tenant admin richiesto.",
        )
    return current_user


async def require_admin_or_tenant_admin(
    current_user: CurrentUserResponse = Depends(get_active_user),
) -> CurrentUserResponse:
    """Verifica che l'utente corrente abbia ruolo admin o tenant admin."""
    if current_user.role_code not in {ADMIN_ROLE, TENANT_ADMIN_ROLE}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ruolo admin o tenant admin richiesto.",
        )
    return current_user


async def get_sse_user(
    token: str | None = Query(default=None, alias="token"),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    auth_service: AuthService = Depends(get_auth_service),
) -> CurrentUserResponse:
    """Dependency per endpoint SSE: accetta token da header Bearer o query param.

    EventSource del browser non supporta header custom, quindi il token puo
    essere passato come ?token=<access_token> nell'URL della connessione.
    """
    raw_token = credentials.credentials if credentials else token
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticazione richiesta.",
        )
    try:
        user = await auth_service.get_current_user(raw_token)
    except (InvalidTokenError, InactiveUserError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Utente non attivo.",
        )
    return user


