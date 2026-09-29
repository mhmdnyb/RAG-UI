"""Shared SQLAlchemy engines, one per database URL."""

from sqlalchemy import create_engine as _create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.common.config import settings

_engines: dict[str, Engine] = {}


def get_engine(database_url: str | None = None) -> Engine:
    url = database_url or settings.database_url
    engine = _engines.get(url)
    if engine is None:
        engine = _create_engine(
            url,
            pool_pre_ping=True,
            pool_size=settings.db_pool_size,
            max_overflow=settings.db_max_overflow,
            pool_timeout=settings.db_pool_timeout_seconds,
            connect_args={
                "application_name": "rag-service",
                "options": f"-c statement_timeout={settings.db_statement_timeout_ms}",
            },
        )
        _engines[url] = engine
    return engine


def dispose_engine() -> None:
    while _engines:
        _, engine = _engines.popitem()
        engine.dispose()


def get_session() -> Session:
    return sessionmaker(bind=get_engine())()
