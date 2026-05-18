"""Route per la lettura delle distinte base."""

from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.orm import Session

from app.api.deps.rbac import RequirePermission
from app.core.db import get_db_session
from app.repositories.core.bom_repository import BomRepository
from app.schemas.auth.responses import CurrentUserResponse
from app.schemas.bom.responses import BomResponse
from app.services.bom.bom_service import BomService

router = APIRouter(tags=["BOM"])


async def resolve_bom_tenant_id(session: Session, bom_id: str) -> str | None:
    """Restituisce il tenant proprietario della distinta base richiesta."""
    repository = BomRepository(session)
    return await repository.get_bom_tenant_id(bom_id)


def get_bom_service(session: Session = Depends(get_db_session)) -> BomService:
    """Restituisce il servizio applicativo BOM."""
    return BomService(session)


@router.get(
    "/{bom_id}",
    response_model=BomResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Distinta base restituita con successo."},
        401: {"description": "Autenticazione richiesta o token non valido."},
        403: {"description": "Permesso o tenant non consentiti."},
        404: {"description": "Distinta base non trovata."},
    },
    summary="Legge una distinta base tenant-aware",
)
async def get_bom(
    bom_id: str = Path(
        min_length=1,
        max_length=36,
        description="Identificativo della distinta base richiesta.",
        examples=["c4c2b9df-cf80-4938-a1ea-369862bd6bd6"],
    ),
    _: CurrentUserResponse = Depends(
        RequirePermission(
            "bom",
            "read",
            resource_id_param_name="bom_id",
            tenant_resolver=resolve_bom_tenant_id,
        )
    ),
    bom_service: BomService = Depends(get_bom_service),
) -> BomResponse:
    """Restituisce una distinta base accessibile a worker, manager e admin autorizzati."""
    return await bom_service.get_bom(bom_id)
