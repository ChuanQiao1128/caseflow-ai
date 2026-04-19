from __future__ import annotations

from uuid import UUID

from caseflow_api.api.schemas import FollowUpEmailDraftRead


def test_follow_up_email_draft_read_is_explicitly_draft_only() -> None:
    payload = FollowUpEmailDraftRead(
        matter_id=UUID("11111111-1111-1111-1111-111111111111"),
        subject="Follow-up on settlement documents",
        body="Kia ora, just following up on the settlement documents.",
        status="draft_only",
    )

    assert payload.matter_id == UUID("11111111-1111-1111-1111-111111111111")
    assert payload.subject.startswith("Follow-up")
    assert "review" in payload.disclaimer.lower()
    assert "before sending" in payload.disclaimer.lower()
    assert payload.status == "draft_only"
