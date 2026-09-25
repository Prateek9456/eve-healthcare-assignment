import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "sqlite://"

import app.database as database_module
from app.config import get_settings
from app.database import Base, get_db

get_settings.cache_clear()

TEST_ENGINE = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)
database_module.engine = TEST_ENGINE

from app.main import app


@pytest.fixture(autouse=True)
def setup_database() -> Generator[None, None, None]:
    Base.metadata.create_all(bind=TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=TEST_ENGINE)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    signup_payload = {
        "email": "patient@example.com",
        "full_name": "Test Patient",
        "password": "securepass123",
    }
    client.post("/auth/signup", json=signup_payload)
    login_response = client.post(
        "/auth/login",
        json={"email": signup_payload["email"], "password": signup_payload["password"]},
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def centre_with_test(client: TestClient) -> dict:
    response = client.post(
        "/centres",
        json={
            "name": "EVE Diagnostics Hauz Khas",
            "location": "Hauz Khas, New Delhi",
            "tests": [{"name": "Complete Blood Count", "price": "499.00"}],
        },
    )
    data = response.json()
    return {"centre_id": data["id"], "test_id": data["tests"][0]["id"]}
