from collections.abc import Generator
from sqlalchemy.orm import Session
from app.db.session import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency providing a scoped SQLAlchemy session per request.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
