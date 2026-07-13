"""
Database initialization utilities.

This module is primarily used during development
and testing.

In production, database schema changes should
always be managed through Alembic migrations.
"""

from sqlalchemy.exc import SQLAlchemyError

from app.database.base import Base
from app.database.models import *  # noqa: F401,F403
from app.database.session import engine


def create_database() -> None:
    """
    Create all database tables.

    Intended for development/testing.
    """

    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully.")

    except SQLAlchemyError as e:
        print(f"❌ Database initialization failed: {e}")
        raise
