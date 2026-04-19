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


def test_approval_queue_actions_write_audit_logs(client: TestClient) -> None:
    org, matter = _create_org_matter(client, "Audit Queue Law", "Matter Audit Queue")

    create_response = client.post(
        f"/organisations/{org['id']}/matters/{matter['id']}/approval-queue",
        json={
            "item_type": "follow_up_email_draft",
            "subject": "Draft subject",
            "body": "Draft body",
            "source_item_id": str(uuid4()),
        },
    )
    assert create_response.status_code == 201
    item = create_response.json()

    approve_response = client.post(
        f"/organisations/{org['id']}/matters/{matter['id']}/approval-queue/{item['id']}/approve",
        json={"reviewer_notes": "Approved"},
    )
    assert approve_response.status_code == 200

    logs_response = client.get(f"/organisations/{org['id']}/matters/{matter['id']}/audit-logs")
    assert logs_response.status_code == 200
    actions = [entry["action"] for entry in logs_response.json()]
    assert "approval_queue.created" in actions
    assert "approval_queue.approved" in actions
