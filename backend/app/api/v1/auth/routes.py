"""Route del modulo Auth."""

from fastapi import APIRouter, Depends, status

from app.api.deps.auth import get_active_user, get_auth_service
from app.schemas.auth.requests import LoginRequest, RefreshTokenRequest
from app.schemas.auth.responses import (
    CurrentUserResponse,
    LogoutResponse,
    TokenPairResponse,
)
from app.services.auth.auth_service import AuthService

router = APIRouter(tags=["Auth"])


@router.post(
    "/login",
    response_model=TokenPairResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Utente autenticato con successo."},
        400: {"description": "Payload della richiesta non valido."},
        401: {"description": "Credenziali non valide."},
        403: {"description": "Utente non attivo."},
    },
    summary="Autentica un utente",
)
async def login(
    payload: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenPairResponse:
    """Autentica un utente e restituisce access token e refresh token.

    Le credenziali vengono validate contro il database PostgreSQL e il sistema
    restituisce token JWT reali associati all'utente autenticato.
    """
    return await auth_service.login(payload)


@router.post(
    "/refresh",
    response_model=TokenPairResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Access token aggiornato con successo."},
        400: {"description": "Payload della richiesta non valido."},
        401: {"description": "Refresh token non valido."},
    },
    summary="Aggiorna un access token",
)
async def refresh_token(
    payload: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenPairResponse:
    """Aggiorna un access token usando un refresh token valido.

    Il refresh token deve appartenere a una sessione attiva persistita e non
    deve risultare revocato.
    """
    return await auth_service.refresh(payload)


@router.post(
    "/logout",
    response_model=LogoutResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Logout completato con successo."},
        401: {"description": "Autenticazione richiesta o token non valido."},
        403: {"description": "Un utente non attivo non puo completare l'operazione."},
    },
    summary="Esegue il logout dell'utente corrente",
)
async def logout(
    current_user: CurrentUserResponse = Depends(get_active_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> LogoutResponse:
    """Esegue il logout dell'utente autenticato corrente.

    L'endpoint e protetto e richiede un bearer token valido.
    """
    return await auth_service.logout(current_user)


@router.get(
    "/me",
    response_model=CurrentUserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Utente autenticato corrente restituito con successo."},
        401: {"description": "Autenticazione richiesta o token non valido."},
        403: {"description": "Un utente non attivo non puo accedere a questo endpoint."},
    },
    summary="Restituisce l'utente corrente",
)
async def me(
    current_user: CurrentUserResponse = Depends(get_active_user),
) -> CurrentUserResponse:
    """Restituisce il profilo dell'utente autenticato corrente.

    L'endpoint risolve il bearer token ed espone ruolo effettivo e insieme
    dei permessi usati dal backend.
    """
    return current_user
