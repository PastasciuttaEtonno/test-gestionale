"""Route del modulo Articoli."""

from fastapi import APIRouter, Depends, Query, status
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.api.deps.events import get_event_publisher
from app.api.deps.rbac import RequirePermission
from app.core.db import get_db_session
from app.core.redis import get_redis_client
from app.repositories.core.articolo_repository import ArticoloRepository
from app.repositories.core.categoria_articolo_repository import CategoriaArticoloRepository
from app.schemas.articoli.requests import (
    ArticoloCreateRequest,
    ArticoloListParams,
    ArticoloUpdateRequest,
    CategoriaCreateRequest,
    CategoriaUpdateRequest,
)
from app.schemas.articoli.responses import (
    ArticoloListResponse,
    ArticoloResponse,
    CategoriaListResponse,
    CategoriaResponse,
)
from app.schemas.auth.responses import CurrentUserResponse
from app.services.articoli.articolo_service import ArticoloService
from app.services.articoli.categoria_service import CategoriaService
from app.services.events.event_publisher import EventPublisher

router = APIRouter(tags=["Articoli"])

_read = RequirePermission("articoli", "read")
_write = RequirePermission("articoli", "write")
_delete = RequirePermission("articoli", "delete")


def _categoria_service(session: Session = Depends(get_db_session)) -> CategoriaService:
    return CategoriaService(CategoriaArticoloRepository(session))


def _articolo_service(
    session: Session = Depends(get_db_session),
    redis_client: Redis = Depends(get_redis_client),
    event_publisher: EventPublisher = Depends(get_event_publisher),
) -> ArticoloService:
    return ArticoloService(
        ArticoloRepository(session),
        CategoriaArticoloRepository(session),
        redis_client=redis_client,
        event_publisher=event_publisher,
    )


# ── Categorie ────────────────────────────────────────────────────────────────
# NB: dichiarate prima delle route /{articolo_id} per evitare che "categorie"
# venga interpretato come un articolo_id.


@router.get(
    "/categorie",
    response_model=CategoriaListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Lista categorie restituita con successo."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso articoli.read richiesto."},
    },
    summary="Elenca le categorie articolo del tenant",
)
def list_categorie(
    is_active: bool = Query(default=True, description="Filtra per stato attivo."),
    current_user: CurrentUserResponse = Depends(_read),
    service: CategoriaService = Depends(_categoria_service),
) -> CategoriaListResponse:
    """Restituisce le categorie articolo del tenant corrente."""
    return service.list_categorie(current_user.tenant_id, is_active=is_active)


@router.post(
    "/categorie",
    response_model=CategoriaResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Categoria creata con successo."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso articoli.write richiesto."},
        409: {"description": "Nome categoria gia esistente nel tenant."},
    },
    summary="Crea una categoria articolo",
)
def create_categoria(
    payload: CategoriaCreateRequest,
    current_user: CurrentUserResponse = Depends(_write),
    service: CategoriaService = Depends(_categoria_service),
) -> CategoriaResponse:
    """Crea una nuova categoria articolo nel tenant corrente."""
    return service.create_categoria(current_user.tenant_id, payload)


@router.patch(
    "/categorie/{categoria_id}",
    response_model=CategoriaResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Categoria aggiornata con successo."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso articoli.write richiesto."},
        404: {"description": "Categoria non trovata."},
        409: {"description": "Nome categoria gia esistente nel tenant."},
    },
    summary="Aggiorna una categoria articolo",
)
def update_categoria(
    categoria_id: str,
    payload: CategoriaUpdateRequest,
    current_user: CurrentUserResponse = Depends(_write),
    service: CategoriaService = Depends(_categoria_service),
) -> CategoriaResponse:
    """Aggiorna parzialmente una categoria del tenant corrente."""
    return service.update_categoria(current_user.tenant_id, categoria_id, payload)


@router.delete(
    "/categorie/{categoria_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Categoria disattivata con successo."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso articoli.delete richiesto."},
        404: {"description": "Categoria non trovata."},
        409: {"description": "Categoria in uso da articoli attivi."},
    },
    summary="Disattiva una categoria articolo",
)
def delete_categoria(
    categoria_id: str,
    current_user: CurrentUserResponse = Depends(_delete),
    service: CategoriaService = Depends(_categoria_service),
) -> None:
    """Disattiva la categoria; bloccata con 409 se usata da articoli attivi."""
    service.delete_categoria(current_user.tenant_id, categoria_id)


# ── Articoli ───────────────────────────────────────────────────────────────


@router.get(
    "",
    response_model=ArticoloListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Lista articoli restituita con successo."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso articoli.read richiesto."},
    },
    summary="Elenca gli articoli del tenant",
)
def list_articoli(
    categoria_id: str | None = Query(default=None, description="Filtra per categoria."),
    is_active: bool = Query(default=True, description="Filtra per stato attivo."),
    q: str | None = Query(default=None, description="Ricerca su codice e descrizione."),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: CurrentUserResponse = Depends(_read),
    service: ArticoloService = Depends(_articolo_service),
) -> ArticoloListResponse:
    """Restituisce la lista paginata degli articoli del tenant corrente."""
    params = ArticoloListParams(
        categoria_id=categoria_id, is_active=is_active, q=q, skip=skip, limit=limit
    )
    return service.list_articoli(current_user.tenant_id, params)


@router.post(
    "",
    response_model=ArticoloResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Articolo creato con successo."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso articoli.write richiesto."},
        404: {"description": "Categoria non trovata nel tenant."},
        409: {"description": "Codice articolo gia esistente nel tenant."},
        422: {"description": "Dati non validi (es. aliquota IVA non ammessa)."},
    },
    summary="Crea un nuovo articolo",
)
async def create_articolo(
    payload: ArticoloCreateRequest,
    current_user: CurrentUserResponse = Depends(_write),
    service: ArticoloService = Depends(_articolo_service),
) -> ArticoloResponse:
    """Crea un nuovo articolo nel tenant corrente e notifica i client via SSE."""
    return await service.create_articolo(current_user.tenant_id, payload)


@router.get(
    "/{articolo_id}",
    response_model=ArticoloResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Articolo restituito con successo."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso articoli.read richiesto."},
        404: {"description": "Articolo non trovato."},
    },
    summary="Dettaglio articolo",
)
def get_articolo(
    articolo_id: str,
    current_user: CurrentUserResponse = Depends(_read),
    service: ArticoloService = Depends(_articolo_service),
) -> ArticoloResponse:
    """Restituisce il dettaglio di un articolo del tenant corrente."""
    return service.get_articolo(current_user.tenant_id, articolo_id)


@router.patch(
    "/{articolo_id}",
    response_model=ArticoloResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Articolo aggiornato con successo."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso articoli.write richiesto."},
        404: {"description": "Articolo o categoria non trovati."},
        409: {"description": "Codice duplicato o conflitto di versione (optimistic lock)."},
    },
    summary="Aggiorna un articolo",
)
async def update_articolo(
    articolo_id: str,
    payload: ArticoloUpdateRequest,
    current_user: CurrentUserResponse = Depends(_write),
    service: ArticoloService = Depends(_articolo_service),
) -> ArticoloResponse:
    """Aggiorna un articolo. Richiede `version` per l'optimistic locking (409 se diverge)."""
    return await service.update_articolo(current_user.tenant_id, articolo_id, payload)


@router.delete(
    "/{articolo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Articolo disattivato con successo."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso articoli.delete richiesto."},
        404: {"description": "Articolo non trovato."},
    },
    summary="Disattiva un articolo (soft delete)",
)
async def delete_articolo(
    articolo_id: str,
    current_user: CurrentUserResponse = Depends(_delete),
    service: ArticoloService = Depends(_articolo_service),
) -> None:
    """Esegue il soft-delete impostando is_active = false e notifica via SSE."""
    await service.delete_articolo(current_user.tenant_id, articolo_id)
