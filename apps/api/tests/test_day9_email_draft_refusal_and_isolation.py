from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient

from caseflow_api.retrieval.evidence import EvidenceCitation
from caseflow_api.retrieval.service import MatterRetrievalResult


def _create_org_matter(client: TestClient, name: str, title: str) -> tuple[dict, dict]:
    org = client.post("/organisations", json={"name": name}).json()
    matter = client.post(
        f"/organisations/{org['id']}/matters",
        json={"reference": f"{title}-ref", "title": title},
    ).json()
    return org, matter


def test_email_draft_endpoint_does_not_query_or_use_other_matter_evidence(
    client: TestClient, monkeypatch
) -> None:
    org_a, matter_a = _create_org_matter(client, "Draft Law A", "Matter Draft A")
    org_b, matter_b = _create_org_matter(client, "Draft Law B", "Matter Draft B")

    calls: list[tuple[UUID, UUID, str]] = []

    def fake_search_matter_evidence(
        *, db, organisation_id, matter_id, query, limit=5, max_distance=0.95
    ):
        calls.append((organisation_id, matter_id, query))
        if matter_id == UUID(matter_b["id"]):
            raise AssertionError("Matter A draft must not query matter B evidence")

        return MatterRetrievalResult(
            organisation_id=organisation_id,
            matter_id=matter_id,
            query=query,
            confidence="high",
            has_evidence=True,
            results=[
                EvidenceCitation(
                    chunk_id=UUID("11111111-1111-1111-1111-111111111111"),
                    document_id=UUID("22222222-2222-2222-2222-222222222222"),
                    page_number=3,
                    chunk_index=1,
                    content="Settlement date: 30 April 2026.",
                    score=0.12,
                    citation="document 22222222-2222-2222-2222-222222222222 (page 3, chunk 1)",
                )
            ],
        )

    monkeypatch.setattr(
        "caseflow_api.extraction.service.search_matter_evidence", fake_search_matter_evidence
    )

    response = client.post(f"/organisations/{org_a['id']}/matters/{matter_a['id']}/email-draft")

    assert response.status_code == 200
    payload = response.json()
    assert payload["matter_id"] == matter_a["id"]
    assert payload["status"] == "draft_only"
    assert calls
    assert {matter_id for _, matter_id, _ in calls} == {UUID(matter_a["id"])}
    assert org_a["id"] != org_b["id"]
    assert matter_a["id"] != matter_b["id"]
    assert "matter b" not in payload["body"].lower()


def test_email_draft_endpoint_uses_cautious_language_when_evidence_is_sparse(
    client: TestClient, monkeypatch
) -> None:
    org, matter = _create_org_matter(client, "Sparse Draft Law", "Matter Sparse")

    def fake_search_matter_evidence(
        *, db, organisation_id, matter_id, query, limit=5, max_distance=0.95
    ):
        return MatterRetrievalResult(
            organisation_id=organisation_id,
            matter_id=matter_id,
            query=query,
            confidence="low",
            has_evidence=False,
            results=[],
            message="No relevant evidence found",
        )

    monkeypatch.setattr(
        "caseflow_api.extraction.service.search_matter_evidence", fake_search_matter_evidence
    )

    response = client.post(f"/organisations/{org['id']}/matters/{matter['id']}/email-draft")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "draft_only"
    assert "may need further review" in payload["body"].lower()
    assert "insufficient evidence" in payload["body"].lower()
    assert "cannot confirm" in payload["body"].lower()
    assert "approved" not in payload["body"].lower()
    assert "final or legal advice" in payload["body"].lower()
    assert "before sending" in payload["disclaimer"].lower()


def test_email_draft_endpoint_keeps_draft_only_messaging_and_no_approval_language(
    client: TestClient,
) -> None:
    org, matter = _create_org_matter(client, "Messaging Draft Law", "Matter Messaging")

    response = client.post(f"/organisations/{org['id']}/matters/{matter['id']}/email-draft")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "draft_only"
    assert "draft only" in payload["body"].lower()
    assert "should not be treated as final or legal advice" in payload["body"].lower()
    assert "approved" not in payload["body"].lower()
    assert "legal advice" in payload["body"].lower()
    assert "approval" in payload["disclaimer"].lower()
    assert "before sending" in payload["disclaimer"].lower()
