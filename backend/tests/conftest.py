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

# Integration tokens are encrypted at rest, so the test process needs a real
# Fernet key. Generated per-run: no key is ever committed.
if not os.environ.get("ENCRYPTION_KEY"):
    from cryptography.fernet import Fernet

    os.environ["ENCRYPTION_KEY"] = Fernet.generate_key().decode()

# Never attempt real SMTP from a test run.
os.environ.setdefault("SMTP_HOST", "")
os.environ.setdefault("EMAIL_FROM", "")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.base import Base
from app.database.session import get_db
from app.main import app
from app.core.jwt import create_access_token
from app.core.security import hash_password
from app.models.auth import User

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
        # A real bcrypt hash so password-verification paths can be tested.
        hashed_password=hash_password("Str0ng!Passw0rd"),
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
        hashed_password=hash_password("Str0ng!Passw0rd"),
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


# ---------------------------------------------------------------------------
# Connected Accounts: every provider is replaced by a fake, so no test ever
# reaches an external API (spec §30).
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def fake_providers(monkeypatch):
    """
    Swap the process-wide connector registry for fakes. Returns the fake
    instances so a test can drive failure modes and assert on what was called.
    """
    from app.controllers.integrations.providers import integration_manager
    from tests.integration_fakes import FakeOAuthProvider, FakePublicProvider

    oauth = FakeOAuthProvider()
    public = FakePublicProvider()
    original = dict(integration_manager._connectors)

    replacement = dict(original)
    replacement[oauth.provider_name] = oauth
    replacement[public.provider_name] = public
    monkeypatch.setattr(integration_manager, "_connectors", replacement, raising=False)

    yield {"oauth": oauth, "public": public}


@pytest.fixture(scope="function")
def auth_headers_b(test_user_b):
    token = create_access_token(data={"sub": str(test_user_b.id)})
    return {"Authorization": f"Bearer {token}"}
