from __future__ import annotations

from caseflow_api.api.schemas import (
    ChecklistFindingRead,
    ExtractedFieldRead,
    ReviewBoundednessRead,
    ReviewDecisionRead,
)


def test_review_decision_read_groups_summary_evidence_and_metadata() -> None:
    payload = ReviewDecisionRead(
        review_summary="Human review recommended because the checklist is incomplete.",
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
                status="fail",
                citation="Page 5, clause 7",
                reason="Finance condition not found in the agreement",
            )
        ],
    )

    assert payload.review_summary.startswith("Human review recommended")
    assert payload.overall_status == "needs_human_review"
    assert payload.extracted_fields[0].field_name == "settlement_date"
    assert payload.checklist_findings[0].status == "fail"
    assert payload.boundedness.is_bounded is True
    assert "not legal advice" in payload.boundedness.disclaimer.lower()


def test_review_boundedness_read_makes_scope_explicit() -> None:
    payload = ReviewBoundednessRead()

    assert payload.is_bounded is True
    assert payload.is_legal_advice is False
    assert "human review" in payload.disclaimer.lower()
