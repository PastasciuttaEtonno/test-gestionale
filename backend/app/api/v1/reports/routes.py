"""Route per la generazione asincrona di report."""

from fastapi import APIRouter, Depends, status

from app.api.deps.auth import require_admin_or_tenant_admin
from app.schemas.auth.responses import CurrentUserResponse
from app.schemas.reports.requests import GenerateReportRequest
from app.schemas.reports.responses import GenerateReportAcceptedResponse
from app.services.reports.report_task_service import ReportTaskService

router = APIRouter(tags=["Reports"])


def get_report_task_service() -> ReportTaskService:
    """Restituisce il servizio di orchestrazione dei report asincroni."""
    return ReportTaskService()


@router.post(
    "/generate",
    response_model=GenerateReportAcceptedResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        202: {"description": "Task report accodato con successo."},
        401: {"description": "Autenticazione richiesta o token non valido."},
        403: {"description": "Ruolo insufficiente o tenant non consentito."},
        404: {"description": "Tenant non trovato."},
    },
    summary="Accoda la generazione asincrona di un report",
)
async def generate_report(
    payload: GenerateReportRequest,
    current_user: CurrentUserResponse = Depends(require_admin_or_tenant_admin),
    report_task_service: ReportTaskService = Depends(get_report_task_service),
) -> GenerateReportAcceptedResponse:
    """Accoda un task Celery che genera un report massivo per un tenant."""
    task_id = await report_task_service.enqueue_report_generation(
        tenant_id=payload.tenant_id,
        requested_by=current_user,
    )
    return GenerateReportAcceptedResponse(task_id=task_id)
