"""Servizi applicativi per l'orchestrazione dei report asincroni."""

from celery.result import AsyncResult
from fastapi import HTTPException, status

from app.core.celery_app import celery_app
from app.core.db import get_db_session_context
from app.repositories.security.tenant_repository import TenantRepository
from app.schemas.auth.responses import CurrentUserResponse
from app.schemas.tasks.responses import TaskStatusResponse
from app.tasks.report_tasks import genera_report_massivo_task


class ReportTaskService:
    """Orchestra l'invio e il monitoraggio di task report su Celery."""

    async def enqueue_report_generation(
        self,
        tenant_id: str,
        requested_by: CurrentUserResponse,
    ) -> str:
        """Accoda la generazione report dopo aver validato accesso e tenant."""
        tenant_id_pulito = tenant_id.strip()
        self._validate_tenant_scope(tenant_id_pulito, requested_by)
        await self._assert_tenant_exists(tenant_id_pulito)

        async_result = genera_report_massivo_task.delay(
            tenant_id=tenant_id_pulito,
            requested_by_user_id=requested_by.id,
        )
        return async_result.id

    async def get_task_status(self, task_id: str) -> TaskStatusResponse:
        """Restituisce lo stato corrente di un task Celery."""
        result = AsyncResult(task_id, app=celery_app)
        state = result.state
        meta = result.info if isinstance(result.info, dict) else {}

        if state == "PENDING":
            return TaskStatusResponse(
                task_id=task_id,
                status="pending",
                progress=0,
                message="Task in coda o non ancora acquisito dal worker.",
            )

        if state == "FAILURE":
            return TaskStatusResponse(
                task_id=task_id,
                status="failure",
                progress=int(meta.get("progress", 100)),
                message=str(result.result),
            )

        return TaskStatusResponse(
            task_id=task_id,
            status=state.lower(),
            progress=int(meta.get("progress", 0)),
            message=str(meta.get("message", "Task in elaborazione.")),
            result_url=meta.get("result_url"),
        )

    async def _assert_tenant_exists(self, tenant_id: str) -> None:
        """Verifica che il tenant esista prima di accodare il task."""
        with get_db_session_context() as session:
            tenant_repository = TenantRepository(session)
            tenant = await tenant_repository.get_tenant(tenant_id)
            if tenant is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tenant non trovato.",
                )

    def _validate_tenant_scope(
        self,
        tenant_id: str,
        requested_by: CurrentUserResponse,
    ) -> None:
        """Applica scoping tenant minimo sugli utenti non globali."""
        if requested_by.role_code == "tenant_admin" and requested_by.tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Il tenant admin puo generare report solo per il proprio tenant.",
            )
