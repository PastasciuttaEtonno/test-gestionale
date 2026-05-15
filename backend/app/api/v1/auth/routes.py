"""Route del modulo Auth."""

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

from app.api.deps.auth import get_active_user, get_auth_service
from app.core.config import settings
from app.core.security.request_context import build_security_request_context
from app.schemas.auth.requests import LoginRequest
from app.schemas.auth.responses import (
    AuthSessionResponse,
    CurrentUserResponse,
    LogoutResponse,
)
from app.services.auth.auth_service import AuthService

router = APIRouter(tags=["Auth"])


def _imposta_refresh_cookie(response: Response, refresh_token: str) -> None:
    """Imposta il cookie HttpOnly che conserva il refresh token."""
    response.set_cookie(
        key=settings.refresh_cookie_name,
        value=refresh_token,
        httponly=True,
        secure=settings.refresh_cookie_secure,
        samesite=settings.refresh_cookie_samesite,
        path=settings.refresh_cookie_path,
        max_age=settings.refresh_token_expire_days * 24 * 60 * 60,
    )


def _rimuovi_refresh_cookie(response: Response) -> None:
    """Rimuove il cookie HttpOnly del refresh token."""
    response.delete_cookie(
        key=settings.refresh_cookie_name,
        path=settings.refresh_cookie_path,
        httponly=True,
        secure=settings.refresh_cookie_secure,
        samesite=settings.refresh_cookie_samesite,
    )


@router.post(
    "/login",
    response_model=AuthSessionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Utente autenticato con successo."},
        400: {"description": "Payload della richiesta non valido."},
        401: {"description": "Credenziali non valide."},
        403: {"description": "Utente non attivo."},
        429: {"description": "Troppi tentativi di accesso. Cooldown attivo."},
    },
    summary="Autentica un utente",
)
async def login(
    payload: LoginRequest,
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthSessionResponse:
    """Autentica un utente e restituisce l'access token.

    Le credenziali vengono validate contro il database PostgreSQL e il sistema
    restituisce un access token JWT reale associato all'utente autenticato.
    Il refresh token viene emesso come cookie `HttpOnly`. In caso di troppi
    errori consecutivi dalla stessa coppia identificativo e IP, il login entra
    in cooldown temporaneo.
    """
    result = await auth_service.login(
        payload,
        request_context=build_security_request_context(request),
    )
    _imposta_refresh_cookie(response, result.refresh_token)
    return result.response


@router.post(
    "/refresh",
    response_model=AuthSessionResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Access token aggiornato con successo."},
        401: {"description": "Refresh token non valido o assente."},
    },
    summary="Aggiorna un access token",
)
async def refresh_token(
    request: Request,
    response: Response,
    auth_service: AuthService = Depends(get_auth_service),
) -> AuthSessionResponse:
    """Aggiorna un access token usando il refresh token nel cookie `HttpOnly`.

    Il refresh token deve appartenere a una sessione attiva persistita, non
    deve risultare revocato e viene ruotato a ogni refresh valido.
    """
    refresh_token_value = request.cookies.get(settings.refresh_cookie_name)
    if not refresh_token_value:
        response_vuota = JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": "Refresh token non valido o assente."},
        )
        _rimuovi_refresh_cookie(response_vuota)
        return response_vuota

    try:
        result = await auth_service.refresh(
            refresh_token_value,
            request_context=build_security_request_context(request),
        )
    except HTTPException as exc:
        if exc.status_code == status.HTTP_401_UNAUTHORIZED:
            response_errore = JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail},
            )
            _rimuovi_refresh_cookie(response_errore)
            return response_errore
        raise

    _imposta_refresh_cookie(response, result.refresh_token)
    return result.response


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
    request: Request,
    response: Response,
    current_user: CurrentUserResponse = Depends(get_active_user),
    auth_service: AuthService = Depends(get_auth_service),
) -> LogoutResponse:
    """Esegue il logout dell'utente autenticato corrente.

    L'endpoint e protetto e richiede un bearer token valido.
    """
    logout_response = await auth_service.logout(
        current_user,
        request_context=build_security_request_context(request),
    )
    _rimuovi_refresh_cookie(response)
    return logout_response


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
