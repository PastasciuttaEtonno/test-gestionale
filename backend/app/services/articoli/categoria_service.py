"""Servizio applicativo per le categorie articolo."""

from fastapi import HTTPException, status

from app.models.core.categoria_articolo import CategoriaArticolo
from app.repositories.core.categoria_articolo_repository import CategoriaArticoloRepository
from app.schemas.articoli.requests import CategoriaCreateRequest, CategoriaUpdateRequest
from app.schemas.articoli.responses import CategoriaListResponse, CategoriaResponse


class CategoriaService:
    """Casi d'uso delle categorie articolo, tenant-aware."""

    def __init__(self, repository: CategoriaArticoloRepository) -> None:
        self.repository = repository

    def list_categorie(self, tenant_id: str, *, is_active: bool = True) -> CategoriaListResponse:
        """Restituisce le categorie attive del tenant."""
        items = self.repository.list(tenant_id, is_active=is_active)
        return CategoriaListResponse(
            items=[CategoriaResponse.model_validate(c) for c in items],
            total=len(items),
        )

    def create_categoria(
        self, tenant_id: str, payload: CategoriaCreateRequest
    ) -> CategoriaResponse:
        """Crea una categoria verificando l'unicita' del nome nel tenant."""
        if self.repository.get_by_nome(tenant_id, payload.nome) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Esiste gia una categoria con questo nome.",
            )
        categoria = CategoriaArticolo(
            tenant_id=tenant_id,
            nome=payload.nome,
            descrizione=payload.descrizione,
        )
        saved = self.repository.create(categoria)
        self.repository.session.commit()
        return CategoriaResponse.model_validate(saved)

    def update_categoria(
        self, tenant_id: str, categoria_id: str, payload: CategoriaUpdateRequest
    ) -> CategoriaResponse:
        """Aggiorna parzialmente una categoria del tenant."""
        record = self._get_or_404(tenant_id, categoria_id)
        if payload.nome and payload.nome != record.nome:
            existing = self.repository.get_by_nome(tenant_id, payload.nome)
            if existing is not None and existing.id != record.id:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Esiste gia una categoria con questo nome.",
                )
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(record, field, value)
        saved = self.repository.update(record)
        self.repository.session.commit()
        return CategoriaResponse.model_validate(saved)

    def delete_categoria(self, tenant_id: str, categoria_id: str) -> None:
        """Disattiva una categoria solo se nessun articolo attivo la usa."""
        record = self._get_or_404(tenant_id, categoria_id)
        in_uso = self.repository.count_articoli_attivi(tenant_id, categoria_id)
        if in_uso > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=(
                    f"Categoria in uso da {in_uso} articoli attivi: "
                    "riassegnarli o disattivarli prima."
                ),
            )
        record.is_active = False
        self.repository.update(record)
        self.repository.session.commit()

    def _get_or_404(self, tenant_id: str, categoria_id: str) -> CategoriaArticolo:
        record = self.repository.get(tenant_id, categoria_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria non trovata.",
            )
        return record
