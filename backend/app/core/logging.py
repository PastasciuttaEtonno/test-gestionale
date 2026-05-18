"""Configurazione del logging applicativo."""

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any

from app.core.config import settings
from app.core.request_id import get_request_id

STANDARD_LOG_RECORD_FIELDS = {
    "args",
    "asctime",
    "created",
    "exc_info",
    "exc_text",
    "filename",
    "funcName",
    "levelname",
    "levelno",
    "lineno",
    "module",
    "msecs",
    "message",
    "msg",
    "name",
    "pathname",
    "process",
    "processName",
    "relativeCreated",
    "stack_info",
    "thread",
    "threadName",
}


class RequestContextFilter(logging.Filter):
    """Aggiunge il request id corrente a ogni log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = get_request_id()
        return True


class JsonLogFormatter(logging.Formatter):
    """Formatter JSON minimale per ambienti osservabili."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        extra_fields = {
            key: value
            for key, value in record.__dict__.items()
            if key not in STANDARD_LOG_RECORD_FIELDS and key != "request_id"
        }
        if extra_fields:
            payload["context"] = extra_fields

        return json.dumps(payload, ensure_ascii=True, default=str)


def configure_logging() -> None:
    """Configura il logging principale dell'applicazione."""
    handler = logging.StreamHandler(sys.stdout)
    handler.addFilter(RequestContextFilter())
    if settings.log_json:
        handler.setFormatter(JsonLogFormatter())
    else:
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s %(name)s [request_id=%(request_id)s] %(message)s"
            )
        )

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        handlers=[handler],
        force=True,
    )
