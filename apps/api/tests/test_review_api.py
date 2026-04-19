from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient

from caseflow_api.api.schemas import ChecklistFindingRead, ExtractedFieldRead, ReviewDecisionRead


def _create_org_matter(client: TestClient, name: str, title: str) -> tuple[dict, dict]:
    org = client.post("/organisations", json={"name": name}).json()
    matter = client.post(
        f"/organisations/{org['id']}/matters",
        json={"reference": f"{title}-ref", "title": title},
    ).json()
    return org, matter


def test_review_endpoint_returns_bounded_review_decision(client: TestClient, monkeypatch) -> None:
    org, matter = _create_org_matter(client, "Review Law", "Matter Review A")
    captured: dict[str, object] = {}

    def fake_extract_matter_fields(*, db, organisation_id, matter_id, field_specs):
        captured["extract_organisation_id"] = organisation_id
        captured["extract_matter_id"] = matter_id
        captured["field_specs"] = field_specs
        return type(
            "ExtractionResult",
            (),
            {
                "matter_id": matter_id,
                "extracted_fields": [
                    ExtractedFieldRead(
                        field_name="settlement_date",
                        value="2026-04-30",
                        confidence=0.91,
                        citation="Page 3",
                    )
                ],
            },
        )()

    def fake_evaluate_checklist(*, matter_id, extracted_fields):
        captured["checklist_matter_id"] = matter_id
        captured["checklist_extracted_fields"] = extracted_fields
        return type(
            "ChecklistResult",
            (),
            {
                "matter_id": matter_id,
                "findings": [
                    ChecklistFindingRead(
                        item_name="buyer_purchase_with_mortgage_requires_lender_evidence",
                        status="pass",
                        citation="Page 8",
                        reason="Lender evidence is present",
                    )
                ],
            },
        )()

    def fake_build_review_decision(*, matter_id, extracted_fields, checklist_findings):
        captured["decision_matter_id"] = matter_id
        captured["decision_extracted_fields"] = extracted_fields
        captured["decision_checklist_findings"] = checklist_findings
        return ReviewDecisionRead(
            review_summary="Ready for human review. This is not legal advice or legal approval.",
            overall_status="ready_for_review",
            extracted_fields=extracted_fields,
            checklist_findings=checklist_findings,
        )

    monkeypatch.setattr(
        "caseflow_api.api.routers.review.extract_matter_fields", fake_extract_matter_fields
    )
    monkeypatch.setattr(
        "caseflow_api.api.routers.review.evaluate_checklist", fake_evaluate_checklist
    )
    monkeypatch.setattr(
        "caseflow_api.api.routers.review.build_review_decision", fake_build_review_decision
    )

    response = client.post(f"/organisations/{org['id']}/matters/{matter['id']}/review")

    assert response.status_code == 200
    payload = response.json()
    assert payload["overall_status"] == "ready_for_review"
    assert payload["boundedness"]["is_bounded"] is True
    assert "not legal advice" in payload["boundedness"]["disclaimer"].lower()
    assert payload["review_summary"].startswith("Ready for human review")
    assert captured["extract_organisation_id"] == UUID(org["id"])
    assert captured["extract_matter_id"] == UUID(matter["id"])
    assert captured["checklist_matter_id"] == UUID(matter["id"])
    assert captured["decision_matter_id"] == UUID(matter["id"])


def test_review_endpoint_enforces_matter_scoping(client: TestClient) -> None:
    org_one, matter_one = _create_org_matter(client, "Review Alpha", "Matter Review B")
    org_two, matter_two = _create_org_matter(client, "Review Beta", "Matter Review C")

    response = client.post(f"/organisations/{org_one['id']}/matters/{matter_two['id']}/review")

    assert response.status_code == 404
    assert response.json()["detail"] == "Matter not found"
    assert org_one["id"] != org_two["id"]
    assert matter_one["id"] != matter_two["id"]


def test_review_endpoint_returns_404_for_missing_matter(client: TestClient) -> None:
    org, _matter = _create_org_matter(client, "Review Gamma", "Matter Review D")

    response = client.post(
        f"/organisations/{org['id']}/matters/00000000-0000-0000-0000-000000000000/review"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Matter not found"
