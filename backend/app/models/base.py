"""Esportazioni di supporto per le classi base ORM."""

import uuid as _uuid

from sqlalchemy.dialects.postgresql import UUID as _PG_UUID
from sqlalchemy.types import TypeDecorator

from app.core.db import Base


class UUIDStr(TypeDecorator):
    """UUID nativo PostgreSQL con interfaccia Python str.

    psycopg3 restituisce uuid.UUID anche con as_uuid=False; questo
    TypeDecorator garantisce che il valore Python sia sempre str.
    """

    impl = _PG_UUID(as_uuid=True)
    cache_ok = True

    def process_result_value(self, value, dialect):
        return str(value) if value is not None else None

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        if isinstance(value, _uuid.UUID):
            return value
        return _uuid.UUID(str(value))


__all__ = ["Base", "UUIDStr"]
