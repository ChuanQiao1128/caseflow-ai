from __future__ import annotations

from uuid import UUID

from caseflow_api.api.schemas import (
    ApprovalQueueActionRequest,
    ApprovalQueueItemCreate,
    ApprovalQueueItemRead,
)

M = UUID("11111111-1111-1111-1111-111111111111")
ITEM_ID = UUID("22222222-2222-2222-2222-222222222222")


def test_approval_queue_item_read_represents_pending_draft() -> None:
    item = ApprovalQueueItemRead(
        id=ITEM_ID,
        organisation_id=M,
        matter_id=M,
        item_type="follow_up_email_draft",
        status="pending",
        subject="Draft email",
        body="Kia ora",
        reviewer_notes=None,
    )

    assert item.status == "pending"
    assert item.item_type == "follow_up_email_draft"
    assert item.reviewer_notes is None


def test_approval_queue_item_create_requires_subject_and_body() -> None:
    item = ApprovalQueueItemCreate(
        item_type="follow_up_email_draft",
        subject="Subject",
        body="Body",
        source_item_id="source-123",
    )

    assert item.item_type == "follow_up_email_draft"
    assert item.subject == "Subject"
    assert item.body == "Body"
    assert item.source_item_id == "source-123"


def test_approval_queue_action_request_accepts_reviewer_notes() -> None:
    request = ApprovalQueueActionRequest(reviewer_notes="Looks good")

    assert request.reviewer_notes == "Looks good"


def test_approval_queue_item_defaults_reviewer_notes_to_none() -> None:
    item = ApprovalQueueItemRead(
        id=ITEM_ID,
        organisation_id=M,
        matter_id=M,
        item_type="follow_up_email_draft",
        status="needs_changes",
        subject="Draft email",
        body="Kia ora",
    )

    assert item.status == "needs_changes"
    assert item.reviewer_notes is None
