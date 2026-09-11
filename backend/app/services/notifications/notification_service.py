"""Servizio applicativo per la creazione e gestione delle notifiche."""

import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.core.notification_repository import NotificationRepository
from app.schemas.auth.responses import CurrentUserResponse
from app.schemas.events.sse import EventTypes
from app.schemas.notifications.responses import (
    MarkReadResponse,
    NotificationListResponse,
    NotificationResponse,
)
from app.services.events.event_publisher import EventPublisher


class NotificationService:
    """Orchestra creazione, lettura e marcatura delle notifiche."""

    def __init__(self, session: Session) -> None:
        self._session = session
        self._repo = NotificationRepository(session)

    async def create_and_publish(
        self,
        *,
        event_type: str,
        title: str,
        body: str,
        publisher: EventPublisher,
        user_id: str | None = None,
        tenant_id: str | None = None,
        extra_payload: dict | None = None,
    ) -> NotificationResponse:
        """Persiste la notifica e la pubblica sul bus SSE."""
        payload_json = json.dumps(extra_payload, ensure_ascii=False) if extra_payload else None

        notification = self._repo.create(
            event_type=event_type,
            title=title,
            body=body,
            user_id=user_id,
            tenant_id=tenant_id,
            payload_json=payload_json,
        )
        self._session.commit()
        self._session.refresh(notification)

        sse_payload = {
            "id": notification.id,
            "event_type": notification.event_type,
            "title": notification.title,
            "body": notification.body,
            "payload": extra_payload,
            "is_read": False,
            "created_at": notification.created_at.isoformat(),
        }

        if tenant_id:
            await publisher.publish_to_tenant(tenant_id, EventTypes.NOTIFICATION_NEW, sse_payload)
        elif user_id:
            await publisher.publish_to_user(user_id, EventTypes.NOTIFICATION_NEW, sse_payload)
        else:
            await publisher.publish_to_admin(EventTypes.NOTIFICATION_NEW, sse_payload)

        return NotificationResponse.model_validate(notification)

    def list_notifications(
        self,
        current_user: CurrentUserResponse,
        *,
        limit: int = 30,
        offset: int = 0,
    ) -> NotificationListResponse:
        """Restituisce le notifiche visibili all'utente con conteggio non lette."""
        items = self._repo.get_for_user(
            current_user.id,
            current_user.tenant_id,
            limit=limit,
            offset=offset,
        )
        unread_count = self._repo.count_unread(current_user.id, current_user.tenant_id)
        return NotificationListResponse(
            items=[NotificationResponse.model_validate(n) for n in items],
            unread_count=unread_count,
            total=len(items),
        )

    def mark_read(
        self,
        notification_id: str,
        current_user: CurrentUserResponse,
    ) -> MarkReadResponse:
        """Segna una singola notifica come letta dopo aver verificato l'accesso."""
        notification = self._repo.get_by_id(notification_id)
        if notification is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Notifica non trovata.",
            )
        self._assert_readable(notification, current_user)
        if not notification.is_read:
            self._repo.mark_read(notification)
            self._session.commit()
        return MarkReadResponse(updated=1)

    def mark_all_read(self, current_user: CurrentUserResponse) -> MarkReadResponse:
        """Segna tutte le notifiche visibili all'utente come lette."""
        updated = self._repo.mark_all_read(current_user.id, current_user.tenant_id)
        self._session.commit()
        return MarkReadResponse(updated=updated)

    def _assert_readable(
        self,
        notification,
        current_user: CurrentUserResponse,
    ) -> None:
        """Verifica che l'utente abbia accesso alla notifica."""
        owned_by_user = notification.user_id == current_user.id
        owned_by_tenant = (
            notification.user_id is None and notification.tenant_id == current_user.tenant_id
        )
        global_broadcast = notification.user_id is None and notification.tenant_id is None
        if not (owned_by_user or owned_by_tenant or global_broadcast):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Accesso alla notifica non consentito.",
            )
