"""Route del modulo Bolle / DDT."""

from fastapi import APIRouter, Depends, Query, status
from redis.asyncio import Redis
from sqlalchemy.orm import Session

from app.api.deps.events import get_event_publisher
from app.api.deps.rbac import RequirePermission
from app.core.db import get_db_session
from app.core.redis import get_redis_client
from app.repositories.core.anagrafica_repository import AnagraficaRepository
from app.repositories.core.articolo_repository import ArticoloRepository
from app.repositories.core.bolla_repository import BollaRepository
from app.schemas.auth.responses import CurrentUserResponse
from app.schemas.bolle.requests import (
    BollaCreateRequest,
    BollaListParams,
    BollaUpdateRequest,
    RigaCreateRequest,
    RigaUpdateRequest,
)
from app.schemas.bolle.responses import BollaListResponse, BollaResponse
from app.services.bolle.bolla_service import BollaService
from app.services.events.event_publisher import EventPublisher

router = APIRouter(tags=["Bolle"])

_read = RequirePermission("bolle", "read")
_write = RequirePermission("bolle", "write")
_delete = RequirePermission("bolle", "delete")


def _service(
    session: Session = Depends(get_db_session),
    redis_client: Redis = Depends(get_redis_client),
    event_publisher: EventPublisher = Depends(get_event_publisher),
) -> BollaService:
    return BollaService(
        BollaRepository(session),
        AnagraficaRepository(session),
        ArticoloRepository(session),
        redis_client=redis_client,
        event_publisher=event_publisher,
    )


@router.get(
    "",
    response_model=BollaListResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Lista bolle restituita con successo."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso bolle.read richiesto."},
    },
    summary="Elenca le bolle del tenant",
)
def list_bolle(
    stato: str | None = Query(default=None, description="bozza | emessa | annullata"),
    anagrafica_id: str | None = Query(default=None, description="Filtra per destinatario."),
    q: str | None = Query(default=None, description="Ricerca sul numero documento."),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: CurrentUserResponse = Depends(_read),
    service: BollaService = Depends(_service),
) -> BollaListResponse:
    """Restituisce la lista paginata delle bolle del tenant corrente."""
    params = BollaListParams(stato=stato, anagrafica_id=anagrafica_id, q=q, skip=skip, limit=limit)
    return service.list_bolle(current_user.tenant_id, params)


@router.post(
    "",
    response_model=BollaResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Bozza di bolla creata con successo."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso bolle.write richiesto."},
        404: {"description": "Anagrafica destinatario non trovata nel tenant."},
    },
    summary="Crea una bozza di bolla",
)
async def create_bolla(
    payload: BollaCreateRequest,
    current_user: CurrentUserResponse = Depends(_write),
    service: BollaService = Depends(_service),
) -> BollaResponse:
    """Crea una nuova bozza di bolla per il destinatario indicato."""
    return await service.create_bolla(current_user.tenant_id, payload)


@router.get(
    "/{bolla_id}",
    response_model=BollaResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Bolla restituita con successo."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso bolle.read richiesto."},
        404: {"description": "Bolla non trovata."},
    },
    summary="Dettaglio bolla",
)
def get_bolla(
    bolla_id: str,
    current_user: CurrentUserResponse = Depends(_read),
    service: BollaService = Depends(_service),
) -> BollaResponse:
    """Restituisce il dettaglio completo di una bolla del tenant, righe incluse."""
    return service.get_bolla(current_user.tenant_id, bolla_id)


@router.patch(
    "/{bolla_id}",
    response_model=BollaResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Testata bolla aggiornata."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso bolle.write richiesto."},
        404: {"description": "Bolla non trovata."},
        409: {"description": "Bolla non in bozza o conflitto di versione."},
    },
    summary="Aggiorna la testata di una bozza",
)
async def update_bolla(
    bolla_id: str,
    payload: BollaUpdateRequest,
    current_user: CurrentUserResponse = Depends(_write),
    service: BollaService = Depends(_service),
) -> BollaResponse:
    """Aggiorna la testata di una bozza (richiede `version`)."""
    return await service.update_bolla(current_user.tenant_id, bolla_id, payload)


@router.delete(
    "/{bolla_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {"description": "Bozza cancellata."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso bolle.delete richiesto."},
        404: {"description": "Bolla non trovata."},
        409: {"description": "Solo le bozze possono essere cancellate."},
    },
    summary="Cancella una bozza",
)
async def delete_bolla(
    bolla_id: str,
    current_user: CurrentUserResponse = Depends(_delete),
    service: BollaService = Depends(_service),
) -> None:
    """Cancella fisicamente una bozza (le bolle emesse si annullano, non si cancellano)."""
    await service.delete_bolla(current_user.tenant_id, bolla_id)


@router.post(
    "/{bolla_id}/emetti",
    response_model=BollaResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Bolla emessa con numero assegnato."},
        400: {"description": "Bolla senza righe."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso bolle.write richiesto."},
        404: {"description": "Bolla non trovata."},
        409: {"description": "Bolla non in bozza o numerazione non configurata."},
    },
    summary="Emette una bozza (assegna il numero)",
)
async def emetti_bolla(
    bolla_id: str,
    current_user: CurrentUserResponse = Depends(_write),
    service: BollaService = Depends(_service),
) -> BollaResponse:
    """Emette la bozza: consuma il numero dalla sequence e congela il documento."""
    return await service.emetti(current_user.tenant_id, bolla_id)


@router.post(
    "/{bolla_id}/annulla",
    response_model=BollaResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Bolla annullata."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso bolle.delete richiesto."},
        404: {"description": "Bolla non trovata."},
        409: {"description": "Solo le bolle emesse possono essere annullate."},
    },
    summary="Annulla una bolla emessa",
)
async def annulla_bolla(
    bolla_id: str,
    current_user: CurrentUserResponse = Depends(_delete),
    service: BollaService = Depends(_service),
) -> BollaResponse:
    """Annulla una bolla emessa (stato terminale, resta a registro)."""
    return await service.annulla(current_user.tenant_id, bolla_id)


# ── Righe (solo su bozza) ────────────────────────────────────────────────


@router.post(
    "/{bolla_id}/righe",
    response_model=BollaResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Riga aggiunta, totali ricalcolati."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso bolle.write richiesto."},
        404: {"description": "Bolla o articolo non trovati."},
        409: {"description": "La bolla non e' in stato bozza."},
    },
    summary="Aggiunge una riga alla bozza",
)
async def add_riga(
    bolla_id: str,
    payload: RigaCreateRequest,
    current_user: CurrentUserResponse = Depends(_write),
    service: BollaService = Depends(_service),
) -> BollaResponse:
    """Aggiunge una riga prendendo lo snapshot dei dati articolo correnti."""
    return await service.add_riga(current_user.tenant_id, bolla_id, payload)


@router.patch(
    "/{bolla_id}/righe/{riga_id}",
    response_model=BollaResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Riga aggiornata, totali ricalcolati."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso bolle.write richiesto."},
        404: {"description": "Bolla o riga non trovata."},
        409: {"description": "La bolla non e' in stato bozza."},
    },
    summary="Aggiorna la quantita' di una riga",
)
async def update_riga(
    bolla_id: str,
    riga_id: str,
    payload: RigaUpdateRequest,
    current_user: CurrentUserResponse = Depends(_write),
    service: BollaService = Depends(_service),
) -> BollaResponse:
    """Aggiorna la quantita' di una riga ricalcolando importo e totali."""
    return await service.update_riga(current_user.tenant_id, bolla_id, riga_id, payload)


@router.delete(
    "/{bolla_id}/righe/{riga_id}",
    response_model=BollaResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Riga rimossa, totali ricalcolati."},
        401: {"description": "Autenticazione richiesta."},
        403: {"description": "Permesso bolle.write richiesto."},
        404: {"description": "Bolla o riga non trovata."},
        409: {"description": "La bolla non e' in stato bozza."},
    },
    summary="Rimuove una riga dalla bozza",
)
async def delete_riga(
    bolla_id: str,
    riga_id: str,
    current_user: CurrentUserResponse = Depends(_write),
    service: BollaService = Depends(_service),
) -> BollaResponse:
    """Rimuove una riga e ricalcola i totali della bolla."""
    return await service.delete_riga(current_user.tenant_id, bolla_id, riga_id)
