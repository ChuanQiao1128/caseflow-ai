from __future__ import annotations

from uuid import UUID

from caseflow_api.api.schemas import (
    ChecklistFindingRead,
    ExtractedFieldRead,
    ReviewDecisionRead,
)
from caseflow_api.email_drafts.service import build_email_draft


def test_build_email_draft_is_draft_only_and_citation_aware() -> None:
    decision = ReviewDecisionRead(
        review_summary="Human review recommended because the finance condition is unclear.",
        overall_status="needs_human_review",
        extracted_fields=[
            ExtractedFieldRead(
                field_name="settlement_date",
                value="2026-04-30",
                confidence=0.92,
                citation="Page 3, paragraph 2",
            )
        ],
        checklist_findings=[
            ChecklistFindingRead(
                item_name="Finance condition included",
                status="unclear",
                citation="Page 5, clause 7",
                reason="No express finance condition was located in the agreement",
            )
        ],
    )

    draft = build_email_draft(
        matter_id=UUID("11111111-1111-1111-1111-111111111111"),
        review_decision=decision,
    )

    assert draft.matter_id == UUID("11111111-1111-1111-1111-111111111111")
    assert draft.status == "draft_only"
    assert "not sent" not in draft.body.lower()
    assert "approved" not in draft.body.lower()
    assert "Page 3, paragraph 2" in draft.body
    assert "Page 5, clause 7" in draft.body
    assert "settlement date" in draft.body.lower()
    assert "finance condition" in draft.body.lower()
    assert "review before sending" in draft.disclaimer.lower()


def test_build_email_draft_uses_cautious_language_when_evidence_is_sparse() -> None:
    decision = ReviewDecisionRead(
        review_summary="Insufficient evidence is available for a bounded human review.",
        overall_status="insufficient_evidence",
        extracted_fields=[],
        checklist_findings=[],
    )

    draft = build_email_draft(
        matter_id=UUID("22222222-2222-2222-2222-222222222222"),
        review_decision=decision,
    )

    assert draft.subject.startswith("Draft")
    assert "may need further review" in draft.body.lower()
    assert "insufficient evidence" in draft.body.lower()
    assert "cannot confirm" in draft.body.lower()
    assert "before sending" in draft.disclaimer.lower()
