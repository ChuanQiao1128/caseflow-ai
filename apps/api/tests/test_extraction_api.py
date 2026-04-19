from __future__ import annotations

from uuid import UUID

from fastapi.testclient import TestClient

from caseflow_api.api.schemas import ExtractedFieldRead, MatterExtractionResponse

ORG_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
MATTER_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
OTHER_ORG_ID = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")
OTHER_MATTER_ID = UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")


def _create_org_matter(client: TestClient, name: str, title: str) -> tuple[dict, dict]:
    org = client.post("/organisations", json={"name": name}).json()
    matter = client.post(
        f"/organisations/{org['id']}/matters",
        json={"reference": f"{title}-ref", "title": title},
    ).json()
    return org, matter


def test_extract_matter_fields_endpoint_returns_structured_payload(
    client: TestClient, monkeypatch
) -> None:
    org, matter = _create_org_matter(client, "Acme Law", "Matter A")
    captured: dict[str, object] = {}

    def fake_extract_matter_fields(*, db, organisation_id, matter_id, field_specs):
        captured["organisation_id"] = organisation_id
        captured["matter_id"] = matter_id
        captured["field_specs"] = field_specs
        return MatterExtractionResponse(
            matter_id=matter_id,
            extracted_fields=[
                ExtractedFieldRead(
                    field_name="settlement_date",
                    value="30 April 2026",
                    confidence=0.9,
                    citation="document 1 (page 3, chunk 1)",
                )
            ],
        )

    monkeypatch.setattr(
        "caseflow_api.api.routers.extraction.extract_matter_fields", fake_extract_matter_fields
    )

    response = client.post(f"/organisations/{org['id']}/matters/{matter['id']}/extract")

    assert response.status_code == 200
    assert captured["organisation_id"] == UUID(org["id"])
    assert captured["matter_id"] == UUID(matter["id"])
    assert captured["field_specs"]
    payload = response.json()
    assert payload["matter_id"] == matter["id"]
    assert payload["extracted_fields"][0]["field_name"] == "settlement_date"
    assert payload["extracted_fields"][0]["value"] == "30 April 2026"
    assert payload["extracted_fields"][0]["confidence"] == 0.9
    assert payload["extracted_fields"][0]["citation"] == "document 1 (page 3, chunk 1)"


def test_extract_matter_fields_endpoint_returns_unclear_when_evidence_missing(
    client: TestClient, monkeypatch
) -> None:
    org, matter = _create_org_matter(client, "Beta Law", "Matter B")

    def fake_extract_matter_fields(*, db, organisation_id, matter_id, field_specs):
        return MatterExtractionResponse(
            matter_id=matter_id,
            extracted_fields=[
                ExtractedFieldRead(
                    field_name="deposit_amount",
                    value=None,
                    confidence=0.0,
                    citation="needs_human_review",
                )
            ],
        )

    monkeypatch.setattr(
        "caseflow_api.api.routers.extraction.extract_matter_fields", fake_extract_matter_fields
    )

    response = client.post(f"/organisations/{org['id']}/matters/{matter['id']}/extract")

    assert response.status_code == 200
    payload = response.json()
    assert payload["extracted_fields"][0]["value"] is None
    assert payload["extracted_fields"][0]["confidence"] == 0.0
    assert payload["extracted_fields"][0]["citation"] == "needs_human_review"


def test_extract_matter_fields_endpoint_enforces_matter_scoping(client: TestClient) -> None:
    org_one, matter_one = _create_org_matter(client, "Gamma Law", "Matter C")
    org_two, matter_two = _create_org_matter(client, "Delta Law", "Matter D")

    response = client.post(f"/organisations/{org_one['id']}/matters/{matter_two['id']}/extract")

    assert response.status_code == 404
    assert response.json()["detail"] == "Matter not found"
    assert org_one["id"] != org_two["id"]
    assert matter_one["id"] != matter_two["id"]
