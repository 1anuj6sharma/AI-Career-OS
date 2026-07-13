from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.

    Every database model in the application
    (User, Job, Resume, Interview, etc.)
    should inherit from this class.
    """

    pass
