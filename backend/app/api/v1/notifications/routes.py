"""Route per il Notification Center."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps.auth import get_active_user
from app.api.deps.events import get_event_publisher
from app.core.db import get_db_session
from app.schemas.auth.responses import CurrentUserResponse
from app.schemas.notifications.responses import (
    MarkReadResponse,
    NotificationListResponse,
    NotificationResponse,
)
from app.services.events.event_publisher import EventPublisher
from app.services.notifications.notification_service import NotificationService

router = APIRouter(tags=["Notifications"])


def get_notification_service(session: Session = Depends(get_db_session)) -> NotificationService:
    """Restituisce il servizio notifiche."""
    return NotificationService(session)


@router.get(
    "",
    response_model=NotificationListResponse,
    status_code=status.HTTP_200_OK,
    summary="Restituisce le notifiche dell'utente corrente",
)
async def list_notifications(
    limit: int = Query(default=30, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: CurrentUserResponse = Depends(get_active_user),
    service: NotificationService = Depends(get_notification_service),
) -> NotificationListResponse:
    """Restituisce le notifiche personali e broadcast del tenant, ordinate per data."""
    return service.list_notifications(current_user, limit=limit, offset=offset)


@router.patch(
    "/{notification_id}/read",
    response_model=MarkReadResponse,
    status_code=status.HTTP_200_OK,
    summary="Segna una notifica come letta",
)
async def mark_notification_read(
    notification_id: str,
    current_user: CurrentUserResponse = Depends(get_active_user),
    service: NotificationService = Depends(get_notification_service),
) -> MarkReadResponse:
    """Imposta is_read=True sulla notifica specificata."""
    return service.mark_read(notification_id, current_user)


@router.post(
    "/read-all",
    response_model=MarkReadResponse,
    status_code=status.HTTP_200_OK,
    summary="Segna tutte le notifiche come lette",
)
async def mark_all_notifications_read(
    current_user: CurrentUserResponse = Depends(get_active_user),
    service: NotificationService = Depends(get_notification_service),
) -> MarkReadResponse:
    """Segna come lette tutte le notifiche visibili all'utente corrente."""
    return service.mark_all_read(current_user)


@router.post(
    "/test",
    response_model=NotificationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Invia una notifica di test (solo sviluppo)",
    include_in_schema=True,
)
async def send_test_notification(
    current_user: CurrentUserResponse = Depends(get_active_user),
    service: NotificationService = Depends(get_notification_service),
    publisher: EventPublisher = Depends(get_event_publisher),
) -> NotificationResponse:
    """Crea una notifica di test per l'utente corrente e la pubblica via SSE."""
    return await service.create_and_publish(
        event_type="system.alert",
        title="Notifica di test",
        body=f"Questa e una notifica di test per l'utente {current_user.username}.",
        publisher=publisher,
        user_id=current_user.id,
        tenant_id=current_user.tenant_id,
    )
