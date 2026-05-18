"""Gestione del request id propagato nel contesto applicativo."""

from contextvars import ContextVar, Token

REQUEST_ID_DEFAULT = "-"
_request_id_context: ContextVar[str] = ContextVar("request_id", default=REQUEST_ID_DEFAULT)


def get_request_id() -> str:
    """Restituisce il request id corrente o un placeholder neutro."""
    return _request_id_context.get()


def set_request_id(request_id: str) -> Token[str]:
    """Imposta il request id corrente nel contesto asincrono."""
    return _request_id_context.set(request_id)


def reset_request_id(token: Token[str]) -> None:
    """Ripristina il contesto precedente del request id."""
    _request_id_context.reset(token)
