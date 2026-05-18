"""Servizio applicativo per lettura distinte base tenant-aware."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.core.bom_repository import BomRepository
from app.schemas.bom.responses import BomResponse


class BomService:
    """Casi d'uso di lettura della distinta base."""

    def __init__(self, session: Session) -> None:
        self.bom_repository = BomRepository(session)

    async def get_bom(self, bom_id: str) -> BomResponse:
        """Restituisce la distinta base richiesta."""
        entity = await self.bom_repository.get_bom(bom_id)
        if entity is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Distinta base non trovata.",
            )

        return BomResponse(
            id=entity.id,
            tenant_id=entity.tenant_id,
            code=entity.code,
            name=entity.name,
            description=entity.description,
            updated_at=entity.updated_at,
        )
