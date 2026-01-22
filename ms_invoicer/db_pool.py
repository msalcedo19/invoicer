from contextlib import contextmanager
from typing import ContextManager, Generator

from sqlalchemy.orm import Session

from ms_invoicer.sql_app.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """Get db."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context() -> ContextManager[Session]:
    """Get db context."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
