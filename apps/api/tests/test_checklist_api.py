from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient

from caseflow_api.api.schemas import ExtractedFieldRead

ORG_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
MATTER_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


def _create_org_matter(client: TestClient, name: str, title: str) -> tuple[dict, dict]:
    org = client.post("/organisations", json={"name": name}).json()
    matter = client.post(
        f"/organisations/{org['id']}/matters",
        json={"reference": f"{title}-ref", "title": title},
    ).json()
    return org, matter


def test_checklist_endpoint_returns_deterministic_findings(client: TestClient, monkeypatch) -> None:
    org, matter = _create_org_matter(client, "Acme Law", "Matter A")
    captured: dict[str, object] = {}

    def fake_extract_matter_fields(*, db, organisation_id, matter_id, field_specs):
        captured["organisation_id"] = organisation_id
        captured["matter_id"] = matter_id
        captured["field_specs"] = field_specs
        return type(
            "Response",
            (),
            {
                "matter_id": matter_id,
                "extracted_fields": [
                    ExtractedFieldRead(
                        field_name="party_role", value="buyer", confidence=1.0, citation="Page 1"
                    ),
                    ExtractedFieldRead(
                        field_name="transaction_type",
                        value="purchase",
                        confidence=1.0,
                        citation="Page 1",
                    ),
                    ExtractedFieldRead(
                        field_name="finance_type",
                        value="mortgage",
                        confidence=1.0,
                        citation="Page 2",
                    ),
                    ExtractedFieldRead(
                        field_name="lender_evidence",
                        value="ANZ pre-approval letter",
                        confidence=0.9,
                        citation="Page 8",
                    ),
                ],
            },
        )()

    monkeypatch.setattr(
        "caseflow_api.api.routers.checklists.extract_matter_fields", fake_extract_matter_fields
    )

    response = client.post(f"/organisations/{org['id']}/matters/{matter['id']}/checklist")

    assert response.status_code == 200
    assert captured["organisation_id"] == UUID(org["id"])
    assert captured["matter_id"] == UUID(matter["id"])
    payload = response.json()
    assert payload["matter_id"] == matter["id"]
    assert payload["findings"]
    finding = payload["findings"][0]
    assert finding["item_name"] == "buyer_purchase_with_mortgage_requires_lender_evidence"
    assert finding["status"] == "pass"
    assert finding["citation"] == "Page 8"


def test_checklist_endpoint_returns_unclear_when_required_evidence_missing(
    client: TestClient, monkeypatch
) -> None:
    org, matter = _create_org_matter(client, "Beta Law", "Matter B")

    def fake_extract_matter_fields(*, db, organisation_id, matter_id, field_specs):
        return type(
            "Response",
            (),
            {
                "matter_id": matter_id,
                "extracted_fields": [
                    ExtractedFieldRead(
                        field_name="party_role", value="buyer", confidence=1.0, citation="Page 1"
                    ),
                    ExtractedFieldRead(
                        field_name="transaction_type",
                        value="purchase",
                        confidence=1.0,
                        citation="Page 1",
                    ),
                    ExtractedFieldRead(
                        field_name="finance_type",
                        value="mortgage",
                        confidence=1.0,
                        citation="Page 2",
                    ),
                ],
            },
        )()

    monkeypatch.setattr(
        "caseflow_api.api.routers.checklists.extract_matter_fields", fake_extract_matter_fields
    )

    response = client.post(f"/organisations/{org['id']}/matters/{matter['id']}/checklist")

    assert response.status_code == 200
    payload = response.json()
    finding = payload["findings"][0]
    assert finding["status"] == "unclear"
    assert finding["reason"] == "Mortgage is indicated, but lender evidence was not found"
    assert finding["citation"] == "Page 2"


def test_checklist_endpoint_enforces_matter_scoping(client: TestClient) -> None:
    org_one, matter_one = _create_org_matter(client, "Gamma Law", "Matter C")
    org_two, matter_two = _create_org_matter(client, "Delta Law", "Matter D")

    response = client.post(f"/organisations/{org_one['id']}/matters/{matter_two['id']}/checklist")

    assert response.status_code == 404
    assert response.json()["detail"] == "Matter not found"
    assert org_one["id"] != org_two["id"]
    assert matter_one["id"] != matter_two["id"]
