import os

os.environ.setdefault(
    "SECRET_KEY", "ai_career_os_super_secret_key_2026_development_123456789"
)
os.environ.setdefault(
    "DATABASE_URL", "sqlite:///:memory:"
)
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
os.environ.setdefault(
    "BACKEND_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.core.jwt import create_access_token
from app.modules.auth.models import User

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    def _get_test_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _get_test_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    user = User(
        first_name="Alice",
        last_name="Engineer",
        email="alice@example.com",
        hashed_password="hashed_secret_password",
        role="user",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_user_b(db_session):
    user = User(
        first_name="Bob",
        last_name="Developer",
        email="bob@example.com",
        hashed_password="hashed_secret_password",
        role="user",
        is_active=True,
        is_verified=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(test_user):
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def auth_headers_b(test_user_b):
    token = create_access_token(data={"sub": str(test_user_b.id)})
    return {"Authorization": f"Bearer {token}"}
