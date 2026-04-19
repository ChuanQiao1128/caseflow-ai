from __future__ import annotations

from uuid import uuid4

from fastapi.testclient import TestClient


def _create_org_matter(client: TestClient, name: str, title: str) -> tuple[dict, dict]:
    org = client.post("/organisations", json={"name": name}).json()
    matter = client.post(
        f"/organisations/{org['id']}/matters",
        json={"reference": f"{title}-ref", "title": title},
    ).json()
    return org, matter


def _queue_item_payload(subject: str = "Draft subject", body: str = "Draft body") -> dict[str, str]:
    return {
        "item_type": "follow_up_email_draft",
        "subject": subject,
        "body": body,
        "source_item_id": str(uuid4()),
    }


def test_approval_queue_api_lists_and_transitions_items(client: TestClient) -> None:
    org, matter = _create_org_matter(client, "Queue Law", "Matter Queue A")

    create_response = client.post(
        f"/organisations/{org['id']}/matters/{matter['id']}/approval-queue",
        json=_queue_item_payload(),
    )
    assert create_response.status_code == 201
    created = create_response.json()
    assert created["status"] == "pending"
    assert created["matter_id"] == matter["id"]

    list_response = client.get(f"/organisations/{org['id']}/matters/{matter['id']}/approval-queue")
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    approve_response = client.post(
        f"/organisations/{org['id']}/matters/{matter['id']}/approval-queue/{created['id']}/approve",
        json={"reviewer_notes": "Approved after checking"},
    )
    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"

    reject_response = client.post(
        f"/organisations/{org['id']}/matters/{matter['id']}/approval-queue/{created['id']}/reject",
        json={"reviewer_notes": "Changed my mind"},
    )
    assert reject_response.status_code == 200
    assert reject_response.json()["status"] == "rejected"



def test_approval_queue_api_enforces_matter_scoping(client: TestClient) -> None:
    org_one, matter_one = _create_org_matter(client, "Queue Alpha", "Matter Queue B")
    org_two, matter_two = _create_org_matter(client, "Queue Beta", "Matter Queue C")

    create_response = client.post(
        f"/organisations/{org_one['id']}/matters/{matter_one['id']}/approval-queue",
        json=_queue_item_payload(),
    )
    created = create_response.json()

    response = client.get(
        f"/organisations/{org_one['id']}/matters/{matter_two['id']}/approval-queue"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Matter not found"

    response = client.post(
        f"/organisations/{org_one['id']}/matters/{matter_two['id']}/approval-queue/{created['id']}/approve",
        json={"reviewer_notes": "wrong matter"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Matter not found"

    assert org_one["id"] != org_two["id"]
    assert matter_one["id"] != matter_two["id"]



def test_approval_queue_api_returns_404_for_missing_matter(client: TestClient) -> None:
    org, _matter = _create_org_matter(client, "Queue Gamma", "Matter Queue D")

    response = client.get(
        f"/organisations/{org['id']}/matters/00000000-0000-0000-0000-000000000000/approval-queue"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Matter not found"
