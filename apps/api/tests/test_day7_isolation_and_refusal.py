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


def test_extraction_on_matter_a_cannot_see_matter_b_evidence(
    client: TestClient,
    db_session: Session,
) -> None:
    org, matter_a = _create_org_matter(client, "Acme Law", "Matter A")
    matter_b = client.post(
        f"/organisations/{org['id']}/matters",
        json={"reference": "Matter B-ref", "title": "Matter B"},
    ).json()

    doc_b = _create_document(client, org["id"], matter_b["id"])
    db_session.add(
        DocumentChunk(
            document_id=doc_b["id"],
            chunk_index=0,
            page_number=2,
            content="Settlement date: 30 April 2026.",
            embedding=embed_text("Settlement date: 30 April 2026."),
        )
    )
    db_session.commit()

    response = client.post(f"/organisations/{org['id']}/matters/{matter_a['id']}/extract")

    assert response.status_code == 200
    payload = response.json()
    settlement_date = next(
        field for field in payload["extracted_fields"] if field["field_name"] == "settlement_date"
    )
    assert settlement_date["value"] is None
    assert settlement_date["confidence"] == 0.0
    assert settlement_date["citation"] == "needs_human_review"


def test_checklist_rules_do_not_pass_when_evidence_is_absent(
    client: TestClient,
    db_session: Session,
) -> None:
    org, matter = _create_org_matter(client, "Beta Law", "Matter B")
    document = _create_document(client, org["id"], matter["id"])

    db_session.add_all(
        [
            DocumentChunk(
                document_id=document["id"],
                chunk_index=0,
                page_number=1,
                content="Party role: buyer.",
                embedding=embed_text("Party role: buyer."),
            ),
            DocumentChunk(
                document_id=document["id"],
                chunk_index=1,
                page_number=1,
                content="Transaction type: purchase.",
                embedding=embed_text("Transaction type: purchase."),
            ),
            DocumentChunk(
                document_id=document["id"],
                chunk_index=2,
                page_number=2,
                content="Finance type: mortgage.",
                embedding=embed_text("Finance type: mortgage."),
            ),
        ]
    )
    db_session.commit()

    response = client.post(f"/organisations/{org['id']}/matters/{matter['id']}/checklist")

    assert response.status_code == 200
    payload = response.json()
    finding = next(
        item
        for item in payload["findings"]
        if item["item_name"] == "buyer_purchase_with_mortgage_requires_lender_evidence"
    )
    assert finding["status"] == "unclear"
    assert finding["reason"] == "Mortgage is indicated, but lender evidence was not found"
    assert finding["citation"]
    assert finding["citation"] != "needs_human_review"


def test_checklist_does_not_fabricate_approval_from_other_matter_evidence(
    client: TestClient,
    db_session: Session,
) -> None:
    org, matter_a = _create_org_matter(client, "Gamma Law", "Matter A")
    matter_b = client.post(
        f"/organisations/{org['id']}/matters",
        json={"reference": "Matter B-ref", "title": "Matter B"},
    ).json()

    doc_b = _create_document(client, org["id"], matter_b["id"])
    db_session.add_all(
        [
            DocumentChunk(
                document_id=doc_b["id"],
                chunk_index=0,
                page_number=1,
                content="Party role: buyer.",
                embedding=embed_text("Party role: buyer."),
            ),
            DocumentChunk(
                document_id=doc_b["id"],
                chunk_index=1,
                page_number=1,
                content="Transaction type: purchase.",
                embedding=embed_text("Transaction type: purchase."),
            ),
            DocumentChunk(
                document_id=doc_b["id"],
                chunk_index=2,
                page_number=2,
                content="Finance type: mortgage.",
                embedding=embed_text("Finance type: mortgage."),
            ),
            DocumentChunk(
                document_id=doc_b["id"],
                chunk_index=3,
                page_number=8,
                content="Lender evidence: ANZ pre-approval letter.",
                embedding=embed_text("Lender evidence: ANZ pre-approval letter."),
            ),
        ]
    )
    db_session.commit()

    response = client.post(f"/organisations/{org['id']}/matters/{matter_a['id']}/checklist")

    assert response.status_code == 200
    payload = response.json()
    findings = payload["findings"]
    assert findings == [] or all(item["status"] != "pass" for item in findings)
