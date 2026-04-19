from __future__ import annotations

from collections.abc import Generator
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

import caseflow_api.models  # noqa: F401
from caseflow_api.database import Base, get_db
from caseflow_api.main import create_app


@pytest.fixture()
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture()
def client(db_session: Session) -> Generator[TestClient, None, None]:
    app = create_app()

    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def test_create_organisation(client: TestClient) -> None:
    response = client.post("/organisations", json={"name": "Acme Law"})

    assert response.status_code == 201
    payload = response.json()
    assert payload["name"] == "Acme Law"
    assert UUID(payload["id"])


def test_create_organisation_duplicate_name_returns_conflict(client: TestClient) -> None:
    client.post("/organisations", json={"name": "Acme Law"})

    response = client.post("/organisations", json={"name": "Acme Law"})

    assert response.status_code == 409
    assert response.json()["detail"] == "Organisation name already exists"


def test_read_organisation(client: TestClient) -> None:
    created = client.post("/organisations", json={"name": "Acme Law"}).json()

    response = client.get(f"/organisations/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_create_matter_and_list_only_for_that_organisation(client: TestClient) -> None:
    org_one = client.post("/organisations", json={"name": "Acme Law"}).json()
    org_two = client.post("/organisations", json={"name": "Beta Law"}).json()

    matter_response = client.post(
        f"/organisations/{org_one['id']}/matters",
        json={"reference": "MAT-001", "title": "Settlement file 1"},
    )

    assert matter_response.status_code == 201
    matter = matter_response.json()
    assert matter["organisation_id"] == org_one["id"]
    assert matter["title"] == "Settlement file 1"

    list_one = client.get(f"/organisations/{org_one['id']}/matters")
    list_two = client.get(f"/organisations/{org_two['id']}/matters")

    assert list_one.status_code == 200
    assert list_two.status_code == 200
    assert [item["id"] for item in list_one.json()] == [matter["id"]]
    assert list_two.json() == []


def test_read_matter_only_under_correct_organisation(client: TestClient) -> None:
    org_one = client.post("/organisations", json={"name": "Acme Law"}).json()
    org_two = client.post("/organisations", json={"name": "Beta Law"}).json()
    matter = client.post(
        f"/organisations/{org_one['id']}/matters",
        json={"reference": "MAT-001", "title": "Settlement file 1"},
    ).json()

    ok_response = client.get(f"/organisations/{org_one['id']}/matters/{matter['id']}")
    wrong_response = client.get(f"/organisations/{org_two['id']}/matters/{matter['id']}")

    assert ok_response.status_code == 200
    assert ok_response.json()["id"] == matter["id"]
    assert wrong_response.status_code == 404


def test_register_document_metadata_and_list_and_audit_logs(client: TestClient) -> None:
    org = client.post("/organisations", json={"name": "Acme Law"}).json()
    matter = client.post(
        f"/organisations/{org['id']}/matters",
        json={"reference": "MAT-001", "title": "Settlement file 1"},
    ).json()

    document_response = client.post(
        f"/organisations/{org['id']}/matters/{matter['id']}/documents",
        json={
            "filename": "settlement-pack.pdf",
            "mime_type": "application/pdf",
            "storage_key": "synthetic/settlement-pack.pdf",
        },
    )

    assert document_response.status_code == 201
    document = document_response.json()
    assert document["matter_id"] == matter["id"]
    assert document["filename"] == "settlement-pack.pdf"

    documents_response = client.get(f"/organisations/{org['id']}/matters/{matter['id']}/documents")
    audit_logs_response = client.get(
        f"/organisations/{org['id']}/matters/{matter['id']}/audit-logs"
    )

    assert documents_response.status_code == 200
    assert documents_response.json() == [document]

    assert audit_logs_response.status_code == 200
    audit_logs = audit_logs_response.json()
    assert len(audit_logs) == 2
    assert {item["action"] for item in audit_logs} == {"matter.created", "document.registered"}
    assert any(item["entity_type"] == "matter" for item in audit_logs)
    assert any(item["entity_type"] == "document" for item in audit_logs)


def test_list_audit_logs_only_returns_requested_matter_logs(client: TestClient) -> None:
    org = client.post("/organisations", json={"name": "Acme Law"}).json()
    first_matter = client.post(
        f"/organisations/{org['id']}/matters",
        json={"reference": "MAT-001", "title": "Settlement file 1"},
    ).json()
    second_matter = client.post(
        f"/organisations/{org['id']}/matters",
        json={"reference": "MAT-002", "title": "Settlement file 2"},
    ).json()

    first_document = client.post(
        f"/organisations/{org['id']}/matters/{first_matter['id']}/documents",
        json={
            "filename": "first-pack.pdf",
            "mime_type": "application/pdf",
            "storage_key": "synthetic/first-pack.pdf",
        },
    ).json()
    second_document = client.post(
        f"/organisations/{org['id']}/matters/{second_matter['id']}/documents",
        json={
            "filename": "second-pack.pdf",
            "mime_type": "application/pdf",
            "storage_key": "synthetic/second-pack.pdf",
        },
    ).json()

    response = client.get(f"/organisations/{org['id']}/matters/{first_matter['id']}/audit-logs")

    assert response.status_code == 200
    audit_logs = response.json()
    assert len(audit_logs) == 2
    assert {item["entity_id"] for item in audit_logs} == {first_matter["id"], first_document["id"]}
    assert second_matter["id"] not in {item["entity_id"] for item in audit_logs}
    assert second_document["id"] not in {item["entity_id"] for item in audit_logs}


def test_document_registration_scoped_to_correct_organisation(client: TestClient) -> None:
    org_one = client.post("/organisations", json={"name": "Acme Law"}).json()
    org_two = client.post("/organisations", json={"name": "Beta Law"}).json()
    matter = client.post(
        f"/organisations/{org_one['id']}/matters",
        json={"reference": "MAT-001", "title": "Settlement file 1"},
    ).json()

    response = client.post(
        f"/organisations/{org_two['id']}/matters/{matter['id']}/documents",
        json={
            "filename": "wrong-org.pdf",
            "mime_type": "application/pdf",
            "storage_key": "synthetic/wrong-org.pdf",
        },
    )

    assert response.status_code == 404
