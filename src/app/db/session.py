from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.domain.models import Base


def _prepare_sqlite_directory(database_path: str) -> None:
    """
    Ensure directories exist for SQLite database files before engine creation.
    """
    if not database_path:
        return

    db_file = Path(database_path)
    if not db_file.is_absolute():
        project_root = Path(__file__).resolve().parents[3]
        db_file = project_root / db_file

    db_file.parent.mkdir(parents=True, exist_ok=True)


engine_url = make_url(settings.database_url)

connect_args: dict[str, object] = {}

if engine_url.get_backend_name() == "sqlite":
    _prepare_sqlite_directory(engine_url.database or "")
    connect_args["check_same_thread"] = False

engine = create_engine(
    settings.database_url, connect_args=connect_args, echo=settings.database_echo
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)
