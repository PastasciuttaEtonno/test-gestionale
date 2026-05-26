"""Endpoint SSE per lo streaming degli eventi applicativi tenant-aware."""

import asyncio
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.api.deps.auth import get_sse_user
from app.core.pubsub import create_pubsub_redis_client
from app.schemas.auth.responses import CurrentUserResponse
from app.services.events.channels import resolve_channel

router = APIRouter(tags=["Events"])

# Secondi senza messaggi prima di inviare un heartbeat al client
_HEARTBEAT_AFTER_TICKS = 15


async def _sse_generator(channel: str) -> AsyncGenerator[str, None]:
    """Generator asincrono che si sottoscrive a un canale Redis e streamma SSE."""
    redis_sub = create_pubsub_redis_client()
    pubsub = redis_sub.pubsub()
    await pubsub.subscribe(channel)
    silent_ticks = 0

    try:
        while True:
            message = await pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=1.0,
            )
            if message and message["type"] == "message":
                yield f"data: {message['data']}\n\n"
                silent_ticks = 0
            else:
                silent_ticks += 1
                if silent_ticks >= _HEARTBEAT_AFTER_TICKS:
                    yield ": heartbeat\n\n"
                    silent_ticks = 0
    except asyncio.CancelledError:
        pass
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.aclose()
        await redis_sub.aclose()


@router.get(
    "/stream",
    summary="Stream SSE degli eventi applicativi",
    description=(
        "Apre uno stream Server-Sent Events autenticato. "
        "Il token puo essere passato come header `Authorization: Bearer <token>` "
        "oppure come query param `?token=<token>` (per compatibilita con EventSource browser)."
    ),
    response_class=StreamingResponse,
    responses={
        200: {"description": "Stream SSE aperto con successo."},
        401: {"description": "Token assente o non valido."},
    },
)
async def sse_event_stream(
    current_user: CurrentUserResponse = Depends(get_sse_user),
) -> StreamingResponse:
    """Apre uno stream SSE per l'utente autenticato, tenant-scoped."""
    channel = resolve_channel(current_user)
    return StreamingResponse(
        _sse_generator(channel),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
