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


def test_review_on_matter_a_cannot_use_matter_b_evidence(
    client: TestClient,
    db_session: Session,
) -> None:
    org, matter_a = _create_org_matter(client, "Refusal Law", "Matter A")
    matter_b = client.post(
        f"/organisations/{org['id']}/matters",
        json={"reference": "Matter B-ref", "title": "Matter B"},
    ).json()

    doc_b = _create_document(client, org["id"], matter_b["id"])
    db_session.add(
        DocumentChunk(
            document_id=doc_b["id"],
            chunk_index=0,
            page_number=8,
            content="Lender evidence: ANZ pre-approval letter for matter B.",
            embedding=embed_text("Lender evidence: ANZ pre-approval letter for matter B."),
        )
    )
    db_session.commit()

    response = client.post(f"/organisations/{org['id']}/matters/{matter_a['id']}/review")

    assert response.status_code == 200
    payload = response.json()
    assert payload["overall_status"] in {"needs_human_review", "insufficient_evidence"}
    assert "matter B" not in payload["review_summary"].lower()
    assert "anz pre-approval letter" not in payload["review_summary"].lower()
    assert payload["boundedness"]["is_bounded"] is True
    assert payload["boundedness"]["is_legal_advice"] is False


def test_review_without_sufficient_evidence_returns_human_review_or_insufficient_evidence(
    client: TestClient,
) -> None:
    org, matter = _create_org_matter(client, "Insufficient Evidence Law", "Matter C")

    response = client.post(f"/organisations/{org['id']}/matters/{matter['id']}/review")

    assert response.status_code == 200
    payload = response.json()
    assert payload["overall_status"] in {"needs_human_review", "insufficient_evidence"}
    assert (
        "insufficient evidence" in payload["review_summary"].lower()
        or "human review" in payload["review_summary"].lower()
    )


def test_review_summary_remains_bounded_and_does_not_imply_legal_approval(
    client: TestClient,
) -> None:
    org, matter = _create_org_matter(client, "Boundedness Law", "Matter D")

    response = client.post(f"/organisations/{org['id']}/matters/{matter['id']}/review")

    assert response.status_code == 200
    payload = response.json()
    summary = payload["review_summary"].lower()
    assert payload["boundedness"]["is_bounded"] is True
    assert "not legal advice" in payload["boundedness"]["disclaimer"].lower()
    assert "legal approval" not in summary
    assert "settlement-ready" not in summary
    assert "bounded human review" in summary or "human review" in summary
