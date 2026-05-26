"""Pubblicazione eventi applicativi su canali Redis Pub/Sub."""

import json
from datetime import UTC, datetime

from redis.asyncio import Redis

from app.services.events.channels import ADMIN_CHANNEL, tenant_channel, user_channel


class EventPublisher:
    """Pubblica eventi tipizzati su canali Redis Pub/Sub.

    Usa il client Redis condiviso dell'app (db 2) per il publish: i canali
    pub/sub sono globali all'istanza Redis, indipendenti dal db index.
    """

    def __init__(self, redis_client: Redis) -> None:
        self._redis = redis_client

    async def publish_to_tenant(
        self,
        tenant_id: str,
        event_type: str,
        payload: dict,
    ) -> None:
        """Pubblica un evento sul canale del tenant specificato."""
        await self._publish(
            channel=tenant_channel(tenant_id),
            event_type=event_type,
            payload=payload,
            tenant_id=tenant_id,
        )

    async def publish_to_admin(self, event_type: str, payload: dict) -> None:
        """Pubblica un evento sul canale admin globale."""
        await self._publish(
            channel=ADMIN_CHANNEL,
            event_type=event_type,
            payload=payload,
        )

    async def publish_to_user(
        self,
        user_id: str,
        event_type: str,
        payload: dict,
        tenant_id: str | None = None,
    ) -> None:
        """Pubblica un evento sul canale personale dell'utente."""
        await self._publish(
            channel=user_channel(user_id),
            event_type=event_type,
            payload=payload,
            tenant_id=tenant_id,
        )

    async def _publish(
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
        await self._redis.publish(channel, message)
