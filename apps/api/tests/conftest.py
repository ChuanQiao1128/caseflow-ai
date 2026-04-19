import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

import caseflow_api.models  # noqa: F401
from caseflow_api.database import Base, get_db
from caseflow_api.main import create_app


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    database_url = os.getenv("CASEFLOW_TEST_DATABASE_URL")
    if not database_url:
        pytest.skip("CASEFLOW_TEST_DATABASE_URL is required for integration tests")

    engine = create_engine(database_url)
    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        Base.metadata.create_all(bind=connection)

    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        with engine.begin() as connection:
            Base.metadata.drop_all(bind=connection)
        engine.dispose()


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
