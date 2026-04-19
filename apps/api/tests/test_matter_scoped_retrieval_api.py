from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from caseflow_api.ai.embeddings import embed_text
from caseflow_api.models import DocumentChunk

pytestmark = pytest.mark.skipif(
    not os.getenv("CASEFLOW_TEST_DATABASE_URL"),
    reason="CASEFLOW_TEST_DATABASE_URL is required for pgvector integration testing",
)


def _create_org_matter(client: TestClient, org_name: str, title: str) -> tuple[dict, dict]:
    org = client.post("/organisations", json={"name": org_name}).json()
    matter = client.post(
        f"/organisations/{org['id']}/matters",
        json={"reference": f"{title}-ref", "title": title},
    ).json()
    return org, matter


def _create_document(client: TestClient, org_id: str, matter_id: str) -> dict:
    return client.post(
        f"/organisations/{org_id}/matters/{matter_id}/documents",
        json={
            "filename": "settlement-pack.pdf",
            "mime_type": "application/pdf",
            "storage_key": f"synthetic/{matter_id}/settlement-pack.pdf",
        },
    ).json()


def test_retrieval_returns_chunks_for_relevant_query(
    client: TestClient, db_session: Session
) -> None:
    org, matter = _create_org_matter(client, "Acme Law", "Matter A")
    document = _create_document(client, org["id"], matter["id"])
    db_session.add(
        DocumentChunk(
            document_id=document["id"],
            chunk_index=0,
            page_number=1,
            content="Loan approval summary. Lender: Harbour Bank.",
            embedding=embed_text("Loan approval summary. Lender: Harbour Bank."),
        )
    )
    db_session.commit()

    response = client.post(
        f"/organisations/{org['id']}/matters/{matter['id']}/search",
        json={"query": "loan approval summary", "limit": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["has_evidence"] is True
    assert payload["confidence"] == "high"
    assert payload["results"]
    first = payload["results"][0]
    assert first["chunk_id"]
    assert first["document_id"] == document["id"]
    assert first["page_number"] == 1
    assert first["chunk_index"] == 0
    assert first["citation"]


def test_retrieval_is_scoped_by_organisation_and_matter(
    client: TestClient,
    db_session: Session,
) -> None:
    org_one, matter_one = _create_org_matter(client, "Acme Law", "Matter A")
    org_two, matter_two = _create_org_matter(client, "Beta Law", "Matter B")
    doc_one = _create_document(client, org_one["id"], matter_one["id"])
    doc_two = _create_document(client, org_two["id"], matter_two["id"])

    db_session.add_all(
        [
            DocumentChunk(
                document_id=doc_one["id"],
                chunk_index=0,
                page_number=1,
                content="Buyer must satisfy finance condition by 30 April 2026.",
                embedding=embed_text("Buyer must satisfy finance condition by 30 April 2026."),
            ),
            DocumentChunk(
                document_id=doc_two["id"],
                chunk_index=0,
                page_number=1,
                content="Vendor must discharge the mortgage before settlement.",
                embedding=embed_text("Vendor must discharge the mortgage before settlement."),
            ),
        ]
    )
    db_session.commit()

    response = client.post(
        f"/organisations/{org_one['id']}/matters/{matter_one['id']}/search",
        json={"query": "vendor must discharge mortgage", "limit": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["results"]
    assert all(result["document_id"] == doc_one["id"] for result in payload["results"])
    assert all(result["chunk_index"] == 0 for result in payload["results"])


def test_retrieval_does_not_leak_across_matters(
    client: TestClient,
    db_session: Session,
) -> None:
    org, matter_one = _create_org_matter(client, "Acme Law", "Matter A")
    matter_two = client.post(
        f"/organisations/{org['id']}/matters",
        json={"reference": "Matter B-ref", "title": "Matter B"},
    ).json()
    doc_one = _create_document(client, org["id"], matter_one["id"])
    doc_two = _create_document(client, org["id"], matter_two["id"])

    db_session.add_all(
        [
            DocumentChunk(
                document_id=doc_one["id"],
                chunk_index=0,
                page_number=1,
                content="Insurance policy starts before settlement.",
                embedding=embed_text("Insurance policy starts before settlement."),
            ),
            DocumentChunk(
                document_id=doc_two["id"],
                chunk_index=0,
                page_number=1,
                content="Loan conditions still outstanding.",
                embedding=embed_text("Loan conditions still outstanding."),
            ),
        ]
    )
    db_session.commit()

    response = client.post(
        f"/organisations/{org['id']}/matters/{matter_one['id']}/search",
        json={"query": "loan conditions outstanding", "limit": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["results"] == [] or all(
        result["document_id"] == doc_one["id"] for result in payload["results"]
    )


def test_no_result_query_returns_low_confidence_response(client: TestClient) -> None:
    org, matter = _create_org_matter(client, "Acme Law", "Matter A")

    response = client.post(
        f"/organisations/{org['id']}/matters/{matter['id']}/search",
        json={"query": "qwerty zxcvbnm unrelated nonsense", "limit": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["has_evidence"] is False
    assert payload["confidence"] == "low"
    assert payload["results"] == []
    assert payload["message"] == "No relevant evidence found"


def test_search_results_include_citation_fields(client: TestClient, db_session: Session) -> None:
    org, matter = _create_org_matter(client, "Acme Law", "Matter A")
    document = _create_document(client, org["id"], matter["id"])
    db_session.add(
        DocumentChunk(
            document_id=document["id"],
            chunk_index=4,
            page_number=3,
            content="Agreement execution page.",
            embedding=embed_text("Agreement execution page."),
        )
    )
    db_session.commit()

    response = client.post(
        f"/organisations/{org['id']}/matters/{matter['id']}/search",
        json={"query": "agreement execution", "limit": 5},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["results"]
    first = payload["results"][0]
    assert first["chunk_id"]
    assert first["document_id"] == document["id"]
    assert first["page_number"] == 3
    assert first["chunk_index"] == 4
    assert first["score"] >= 0.0
    assert first["citation"]
