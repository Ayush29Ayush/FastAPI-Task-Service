import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from alembic.config import Config
from alembic import command
import os

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.config import settings
from app.models.user import User
from app.schemas.user import UserCreate
from app.services import user_service

# --- Database Fixture ---

@pytest.fixture(scope="session")
def test_db_engine():
    """
    Creates a test database engine and runs migrations.
    This has 'session' scope, so it runs once per test session.
    """
    # Ensure we are in test mode
    assert settings.ENV_STATE == "test"
    
    # Get the test database URL
    db_url = settings.get_database_url()
    engine = create_engine(db_url)

    # Find alembic.ini
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    alembic_ini_path = os.path.join(base_dir, "alembic.ini")
    
    # Set up Alembic config
    alembic_cfg = Config(alembic_ini_path)
    alembic_cfg.set_main_option("sqlalchemy.url", db_url)
    alembic_cfg.set_main_option("script_location", os.path.join(base_dir, "migrations"))

    # Drop and recreate all tables
    Base.metadata.drop_all(bind=engine)
    command.upgrade(alembic_cfg, "head")

    yield engine

    # Teardown: Drop all tables after tests are done
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """
    Provides a clean database session for each test.
    This has 'function' scope, so it runs for every single test.
    """
    connection = test_db_engine.connect()
    transaction = connection.begin()
    
    # Create a session
    SessionTesting = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = SessionTesting()

    yield session

    # Teardown: Rollback transaction to clean up
    session.close()
    transaction.rollback()
    connection.close()

# --- API Client Fixture ---

@pytest.fixture(scope="function")
def client(db_session: Session):
    """
    Provides a TestClient for making API requests.
    Overrides the 'get_db' dependency with the test session.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass # Session is managed by the db_session fixture

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as c:
        yield c

# --- Authentication Fixtures ---

@pytest.fixture(scope="function")
def test_user(db_session: Session) -> User:
    """
    Creates a test user in the database.
    """
    user_in = UserCreate(email="test@example.com", password="testpassword123")
    user = user_service.create_user(db=db_session, user_in=user_in)
    return user

@pytest.fixture(scope="function")
def auth_token_header(client: TestClient, test_user: User) -> dict:
    """
    Logs in the test_user and returns the auth header.
    """
    response = client.post(
        f"{settings.API_V1_STR}/auth/login",
        data={"username": test_user.email, "password": "testpassword123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}