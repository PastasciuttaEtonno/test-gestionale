"""Route di amministrazione utenti.

Pattern di autorizzazione: role guard + scoping nel service (NON RequirePermission).
Vedi rationale in ``app/api/deps/rbac.py`` (docstring di modulo). In breve: il super
admin ha ``tenant_id=None`` e deve poter listare/leggere utenti cross-tenant, quindi
il branching della query vive in ``UserService`` (es. ``list_users_by_tenant`` vs
``list_users``), non in una dependency dichiarativa.
"""

from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session

from app.api.deps.auth import require_admin_or_tenant_admin
from app.core.db import get_db_session
from app.schemas.auth.responses import CurrentUserResponse
from app.schemas.users.requests import (
    ChangeUserRoleRequest,
    ChangeUserStatusRequest,
    CreateUserRequest,
    UpdateUserRequest,
)
from app.schemas.users.responses import UserListResponse, UserResponse
from app.services.users.user_service import UserNotFoundError, UserService

router = APIRouter(tags=["Users"])


def get_user_service(session: Session = Depends(get_db_session)) -> UserService:
    """Restituisce la dependency del servizio utenti."""
    return UserService(session)


@router.get(
    "",
    response_model=UserListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Elenco utenti restituito con successo."},
        401: {"description": "Autenticazione richiesta o token non valido."},
        403: {"description": "Ruolo admin o tenant admin richiesto."},
    },
    summary="Elenca gli utenti",
)
async def list_users(
    current_user: CurrentUserResponse = Depends(require_admin_or_tenant_admin),
    user_service: UserService = Depends(get_user_service),
) -> UserListResponse:
    """Restituisce l'elenco corrente degli utenti applicativi.

    Il super admin vede tutti gli utenti, mentre il tenant admin vede solo gli
    utenti appartenenti alla propria organizzazione.
    """
    return await user_service.list_users(actor_user=current_user)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Utente restituito con successo."},
        401: {"description": "Autenticazione richiesta o token non valido."},
        403: {"description": "Ruolo admin o tenant admin richiesto."},
        404: {"description": "Utente non trovato."},
    },
    summary="Recupera un utente per id",
)
async def get_user(
    user_id: str = Path(
        description="Identificativo univoco dell'utente da recuperare.",
        examples=["6c4a6f77-7cc0-4709-a681-96b6cf724f83"],
    ),
    current_user: CurrentUserResponse = Depends(require_admin_or_tenant_admin),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Restituisce un singolo utente applicativo tramite identificativo.

    Il tenant admin puo recuperare solo utenti appartenenti alla propria azienda.
    """
    try:
        return await user_service.get_user(user_id=user_id, actor_user=current_user)
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Utente creato con successo."},
        400: {"description": "Payload della richiesta non valido."},
        401: {"description": "Autenticazione richiesta o token non valido."},
        403: {"description": "Ruolo admin o tenant admin richiesto oppure tenant non consentito."},
        404: {"description": "Ruolo o tenant richiesto non trovato."},
        409: {"description": "Username gia esistente."},
    },
    summary="Crea un utente",
)
async def create_user(
    payload: CreateUserRequest,
    current_user: CurrentUserResponse = Depends(require_admin_or_tenant_admin),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Crea un nuovo utente applicativo.

    La richiesta viene validata, la password viene hashata e il nuovo utente
    viene persistito nello schema `security` di PostgreSQL. Il tenant admin
    puo operare solo sul proprio tenant.
    """
    return await user_service.create_user(payload=payload, actor_user=current_user)


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Utente aggiornato con successo."},
        400: {"description": "Payload della richiesta non valido."},
        401: {"description": "Autenticazione richiesta o token non valido."},
        403: {"description": "Ruolo admin o tenant admin richiesto."},
        404: {"description": "Utente non trovato."},
        409: {"description": "Email gia esistente."},
    },
    summary="Aggiorna un utente",
)
async def update_user(
    payload: UpdateUserRequest,
    user_id: str = Path(
        description="Identificativo univoco dell'utente da aggiornare.",
        examples=["6c4a6f77-7cc0-4709-a681-96b6cf724f83"],
    ),
    current_user: CurrentUserResponse = Depends(require_admin_or_tenant_admin),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Aggiorna i metadati modificabili di un utente.

    In questa fase sono esposti solo email e collegamento futuro al profilo persona.
    Il tenant admin puo aggiornare solo utenti della propria azienda.
    """
    try:
        return await user_service.update_user(
            user_id=user_id, payload=payload, actor_user=current_user
        )
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{user_id}/status",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Stato utente aggiornato con successo."},
        400: {"description": "Payload della richiesta non valido."},
        401: {"description": "Autenticazione richiesta o token non valido."},
        403: {"description": "Ruolo admin o tenant admin richiesto."},
        404: {"description": "Utente non trovato."},
    },
    summary="Modifica lo stato utente",
)
async def change_user_status(
    payload: ChangeUserStatusRequest,
    user_id: str = Path(
        description="Identificativo univoco dell'utente di cui modificare lo stato.",
        examples=["6c4a6f77-7cc0-4709-a681-96b6cf724f83"],
    ),
    current_user: CurrentUserResponse = Depends(require_admin_or_tenant_admin),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Modifica lo stato di attivazione di un account utente.

    L'utente di destinazione deve esistere e il chiamante deve avere privilegi
    compatibili con il proprio perimetro amministrativo.
    """
    try:
        return await user_service.change_status(
            user_id=user_id, payload=payload, actor_user=current_user
        )
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{user_id}/role",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Ruolo utente aggiornato con successo."},
        400: {"description": "Payload della richiesta non valido."},
        401: {"description": "Autenticazione richiesta o token non valido."},
        403: {"description": "Ruolo admin o tenant admin richiesto oppure ruolo non assegnabile."},
        404: {"description": "Utente o ruolo richiesto non trovato."},
    },
    summary="Modifica il ruolo utente",
)
async def change_user_role(
    payload: ChangeUserRoleRequest,
    user_id: str = Path(
        description="Identificativo univoco dell'utente di cui modificare il ruolo.",
        examples=["6c4a6f77-7cc0-4709-a681-96b6cf724f83"],
    ),
    current_user: CurrentUserResponse = Depends(require_admin_or_tenant_admin),
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """Modifica il ruolo assegnato a un utente.

    Il codice ruolo deve essere valido e compatibile con il perimetro del chiamante.
    """
    try:
        return await user_service.change_role(
            user_id=user_id, payload=payload, actor_user=current_user
        )
    except UserNotFoundError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
