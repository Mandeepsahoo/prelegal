from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

db_path = Path(settings.database_path)
db_path.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    """Recreate the database schema from scratch.

    Called on every app startup so the SQLite database is always fresh,
    matching the "created from scratch each time the container starts" spec.
    Dropping/creating tables (rather than deleting the underlying file) avoids
    file-lock issues on platforms, like Windows, where an open DB-API
    connection prevents the file from being removed.
    """
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
