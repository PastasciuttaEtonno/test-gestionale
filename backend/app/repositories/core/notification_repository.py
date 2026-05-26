"""Repository per le notifiche applicative."""

from datetime import UTC, datetime

from sqlalchemy import and_, or_, update
from sqlalchemy.orm import Session

from app.models.core.notification import Notification


class NotificationRepository:
    """Accesso ai dati della tabella core.notifications."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self,
        *,
        event_type: str,
        title: str,
        body: str,
        user_id: str | None = None,
        tenant_id: str | None = None,
        payload_json: str | None = None,
    ) -> Notification:
        """Crea e persiste una nuova notifica."""
        notification = Notification(
            user_id=user_id,
            tenant_id=tenant_id,
            event_type=event_type,
            title=title,
            body=body,
            payload=payload_json,
            is_read=False,
            created_at=datetime.now(UTC),
        )
        self._session.add(notification)
        self._session.flush()
        return notification

    def get_for_user(
        self,
        user_id: str,
        tenant_id: str | None,
        *,
        limit: int = 30,
        offset: int = 0,
    ) -> list[Notification]:
        """Restituisce le notifiche visibili all'utente (personali + broadcast tenant)."""
        conditions = [
            or_(
                Notification.user_id == user_id,
                and_(Notification.user_id.is_(None), Notification.tenant_id == tenant_id),
                and_(
                    Notification.user_id.is_(None),
                    Notification.tenant_id.is_(None),
                ),
            )
        ]
        return (
            self._session.query(Notification)
            .filter(*conditions)
            .order_by(Notification.created_at.desc())
            .offset(offset)
            .limit(limit)
            .all()
        )

    def count_unread(self, user_id: str, tenant_id: str | None) -> int:
        """Conta le notifiche non lette visibili all'utente."""
        return (
            self._session.query(Notification)
            .filter(
                Notification.is_read.is_(False),
                or_(
                    Notification.user_id == user_id,
                    and_(Notification.user_id.is_(None), Notification.tenant_id == tenant_id),
                    and_(
                        Notification.user_id.is_(None),
                        Notification.tenant_id.is_(None),
                    ),
                ),
            )
            .count()
        )

    def get_by_id(self, notification_id: str) -> Notification | None:
        """Cerca una notifica per id."""
        return self._session.get(Notification, notification_id)

    def mark_read(self, notification: Notification) -> None:
        """Segna una notifica come letta."""
        notification.is_read = True
        notification.read_at = datetime.now(UTC)
        self._session.flush()

    def mark_all_read(self, user_id: str, tenant_id: str | None) -> int:
        """Segna come lette tutte le notifiche visibili all'utente. Restituisce il conteggio."""
        result = self._session.execute(
            update(Notification)
            .where(
                Notification.is_read.is_(False),
                or_(
                    Notification.user_id == user_id,
                    and_(Notification.user_id.is_(None), Notification.tenant_id == tenant_id),
                    and_(
                        Notification.user_id.is_(None),
                        Notification.tenant_id.is_(None),
                    ),
                ),
            )
            .values(is_read=True, read_at=datetime.now(UTC))
        )
        return result.rowcount
