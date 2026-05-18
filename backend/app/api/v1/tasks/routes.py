"""Route per il monitoraggio dei task asincroni."""

from fastapi import APIRouter, Depends, status

from app.api.deps.auth import get_active_user
from app.schemas.auth.responses import CurrentUserResponse
from app.schemas.tasks.responses import TaskStatusResponse
from app.services.reports.report_task_service import ReportTaskService

router = APIRouter(tags=["Tasks"])


def get_report_task_service() -> ReportTaskService:
    """Restituisce il servizio per il monitoraggio dei task Celery."""
    return ReportTaskService()


@router.get(
    "/{task_id}/status",
    response_model=TaskStatusResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Stato del task restituito con successo."},
        401: {"description": "Autenticazione richiesta o token non valido."},
    },
    summary="Restituisce lo stato corrente di un task asincrono",
)
async def get_task_status(
    task_id: str,
    _: CurrentUserResponse = Depends(get_active_user),
    report_task_service: ReportTaskService = Depends(get_report_task_service),
) -> TaskStatusResponse:
    """Espone al frontend lo stato corrente del task Celery richiesto."""
    return await report_task_service.get_task_status(task_id)
