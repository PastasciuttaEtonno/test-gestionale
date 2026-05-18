"""Bootstrap del database e primitive SQLAlchemy condivise."""

from collections.abc import Generator, Iterator
from contextlib import contextmanager

from sqlalchemy import MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Classe base dichiarativa per tutti i modelli ORM."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


def get_db_session() -> Generator[Session, None, None]:
    """Restituisce una sessione database per richiesta."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@contextmanager
def get_db_session_context() -> Iterator[Session]:
    """Restituisce una sessione database esplicita per worker o script esterni."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
