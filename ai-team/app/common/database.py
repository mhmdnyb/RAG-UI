"""
Database connection factory.

Provides a shared SQLAlchemy engine and session factory.
Usage:
    from common.database import get_engine, get_session
"""

from sqlalchemy import create_engine as _create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

_engine: Engine | None = None


def get_engine(database_url: str | None = None) -> Engine:
    """
    Return a singleton SQLAlchemy engine.
    If called for the first time, `database_url` must be provided.
    Subsequent calls return the cached engine.
    """
    global _engine
    if _engine is None:
        if database_url is None:
            from common.config import settings
            database_url = settings.database_url
        _engine = _create_engine(database_url, pool_pre_ping=True)
    return _engine


def get_session() -> Session:
    """
    Create and return a new SQLAlchemy session.
    """
    engine = get_engine()
    session_factory = sessionmaker(bind=engine)
    return session_factory()
