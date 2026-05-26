"""Dependency per il bus eventi (EventPublisher)."""

from fastapi import Depends, Request
from redis.asyncio import Redis

from app.core.redis import get_redis_client
from app.services.events.event_publisher import EventPublisher


def get_event_publisher(
    request: Request,
    redis_client: Redis = Depends(get_redis_client),
) -> EventPublisher:
    """Restituisce l'EventPublisher collegato al client Redis condiviso."""
    return EventPublisher(redis_client)
