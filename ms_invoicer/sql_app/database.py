import logging

from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import declarative_base, sessionmaker

from ms_invoicer.config import (
    POOL_MAX_OVERFLOW,
    POOL_PRE_PING,
    POOL_RECYCLE,
    POOL_SIZE,
    POOL_TIMEOUT,
    URL_CONNECTION,
)

log = logging.getLogger(__name__)

engine = create_engine(
    URL_CONNECTION,
    pool_size=POOL_SIZE,
    max_overflow=POOL_MAX_OVERFLOW,
    pool_timeout=POOL_TIMEOUT,
    pool_recycle=POOL_RECYCLE,
    pool_pre_ping=POOL_PRE_PING,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def ensure_database_exists() -> None:
    url = make_url(URL_CONNECTION)
    if not url.database:
        return
    bootstrap_url = url.set(database="postgres")
    bootstrap_engine = create_engine(bootstrap_url, isolation_level="AUTOCOMMIT")
    try:
        with bootstrap_engine.connect() as conn:
            exists = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                {"db_name": url.database},
            ).scalar()
            if not exists:
                log.info(
                    "Creating database",
                    extra={"db_name": url.database, "event": "ensure_database_exists"},
                )
                conn.execute(text(f'CREATE DATABASE "{url.database}"'))
    finally:
        bootstrap_engine.dispose()


def init_db() -> None:
    try:
        ensure_database_exists()
    except Exception:
        log.warning(
            "Skipping database creation",
            exc_info=True,
            extra={"event": "init_db"},
        )
    from ms_invoicer.sql_app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
