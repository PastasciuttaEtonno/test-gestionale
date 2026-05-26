"""Publisher sincrono per contesti Celery (non async)."""

import json
from datetime import UTC, datetime

import redis as redis_sync

from app.core.config import settings
from app.services.events.channels import ADMIN_CHANNEL, tenant_channel, user_channel


class SyncEventPublisher:
    """Pubblica eventi SSE da un contesto sincrono (Celery task).

    Crea una connessione Redis dedicata per la durata del task e la chiude
    al termine tramite close() o context manager.
    """

    def __init__(self) -> None:
        self._redis = redis_sync.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )

    def publish_to_tenant(self, tenant_id: str, event_type: str, payload: dict) -> None:
        """Pubblica un evento sul canale del tenant."""
        self._publish(tenant_channel(tenant_id), event_type, payload, tenant_id=tenant_id)

    def publish_to_admin(self, event_type: str, payload: dict) -> None:
        """Pubblica un evento sul canale admin globale."""
        self._publish(ADMIN_CHANNEL, event_type, payload)

    def publish_to_user(
        self,
        user_id: str,
        event_type: str,
        payload: dict,
        tenant_id: str | None = None,
    ) -> None:
        """Pubblica un evento sul canale personale dell'utente."""
        self._publish(user_channel(user_id), event_type, payload, tenant_id=tenant_id)

    def close(self) -> None:
        """Chiude la connessione Redis."""
        self._redis.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def _publish(
        self,
        channel: str,
        event_type: str,
        payload: dict,
        tenant_id: str | None = None,
    ) -> None:
        message = json.dumps(
            {
                "type": event_type,
                "payload": payload,
                "tenant_id": tenant_id,
                "ts": datetime.now(UTC).isoformat(),
            },
            ensure_ascii=False,
        )
        self._redis.publish(channel, message)
