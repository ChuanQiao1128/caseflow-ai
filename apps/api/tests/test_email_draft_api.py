from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient

from caseflow_api.api.schemas import FollowUpEmailDraftRead, ReviewDecisionRead


def _create_org_matter(client: TestClient, name: str, title: str) -> tuple[dict, dict]:
    org = client.post("/organisations", json={"name": name}).json()
    matter = client.post(
        f"/organisations/{org['id']}/matters",
        json={"reference": f"{title}-ref", "title": title},
    ).json()
    return org, matter


def test_email_draft_endpoint_returns_bounded_draft_email_response(
    client: TestClient, monkeypatch
) -> None:
    org, matter = _create_org_matter(client, "Draft Law", "Matter Draft A")
    captured: dict[str, object] = {}

    def fake_build_review_decision(*, matter_id, extracted_fields, checklist_findings):
        captured["review_matter_id"] = matter_id
        captured["review_extracted_fields"] = extracted_fields
        captured["review_checklist_findings"] = checklist_findings
        return ReviewDecisionRead(
            review_summary="Ready for human review. This is not legal advice or legal approval.",
            overall_status="ready_for_review",
            extracted_fields=[],
            checklist_findings=[],
        )

    def fake_build_email_draft(*, matter_id, review_decision):
        captured["draft_matter_id"] = matter_id
        captured["draft_review_decision"] = review_decision
        return FollowUpEmailDraftRead(
            matter_id=matter_id,
            subject="Draft email for matter 12345678",
            body="Kia ora, this is a draft only for human review.",
            status="draft_only",
            disclaimer=(
                "This is a draft email only and must be reviewed and approved by a "
                "human before sending. It does not send anything automatically."
            ),
        )

    monkeypatch.setattr(
        "caseflow_api.api.routers.email_drafts.build_review_decision", fake_build_review_decision
    )
    monkeypatch.setattr(
        "caseflow_api.api.routers.email_drafts.build_email_draft", fake_build_email_draft
    )

    response = client.post(f"/organisations/{org['id']}/matters/{matter['id']}/email-draft")

    assert response.status_code == 200
    payload = response.json()
    assert payload["matter_id"] == matter["id"]
    assert payload["status"] == "draft_only"
    assert "not sent" not in payload["body"].lower()
    assert "approved" not in payload["body"].lower()
    assert "review" in payload["disclaimer"].lower()
    assert "before sending" in payload["disclaimer"].lower()
    assert captured["review_matter_id"] == UUID(matter["id"])
    assert captured["draft_matter_id"] == UUID(matter["id"])


def test_email_draft_endpoint_enforces_matter_scoping(client: TestClient) -> None:
    org_one, matter_one = _create_org_matter(client, "Draft Alpha", "Matter Draft B")
    org_two, matter_two = _create_org_matter(client, "Draft Beta", "Matter Draft C")

    response = client.post(f"/organisations/{org_one['id']}/matters/{matter_two['id']}/email-draft")

    assert response.status_code == 404
    assert response.json()["detail"] == "Matter not found"
    assert org_one["id"] != org_two["id"]
    assert matter_one["id"] != matter_two["id"]


def test_email_draft_endpoint_returns_404_for_missing_matter(client: TestClient) -> None:
    org, _matter = _create_org_matter(client, "Draft Gamma", "Matter Draft D")

    response = client.post(
        f"/organisations/{org['id']}/matters/00000000-0000-0000-0000-000000000000/email-draft"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Matter not found"
