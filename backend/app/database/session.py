from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,          # Show SQL queries in development
    pool_pre_ping=True,           # Check connection before using it
)

# Session Factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency.

    Creates a new database session for every request
    and automatically closes it afterwards.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()
