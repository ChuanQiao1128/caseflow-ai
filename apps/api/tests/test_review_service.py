from __future__ import annotations

from uuid import UUID

from caseflow_api.api.schemas import ChecklistFindingRead, ExtractedFieldRead
from caseflow_api.review.service import build_review_decision


def test_build_review_decision_marks_unclear_checklist_as_needs_human_review() -> None:
    extracted_fields = [
        ExtractedFieldRead(
            field_name="settlement_date",
            value="2026-04-30",
            confidence=0.92,
            citation="Page 3, paragraph 2",
        )
    ]
    checklist_findings = [
        ChecklistFindingRead(
            item_name="Finance condition included",
            status="unclear",
            citation="Page 5, clause 7",
            reason="Finance condition not found in the agreement",
        )
    ]

    decision = build_review_decision(
        matter_id=UUID("12345678-1234-5678-1234-567812345678"),
        extracted_fields=extracted_fields,
        checklist_findings=checklist_findings,
    )

    assert decision.overall_status == "needs_human_review"
    assert "Human review" in decision.review_summary
    assert "not legal advice" in decision.boundedness.disclaimer.lower()
    assert "Page 3, paragraph 2" in decision.review_summary
    assert decision.extracted_fields == extracted_fields
    assert decision.checklist_findings == checklist_findings


def test_build_review_decision_marks_all_pass_as_ready_for_review_without_overstating() -> None:
    extracted_fields = [
        ExtractedFieldRead(
            field_name="party_role",
            value="buyer",
            confidence=0.88,
            citation="Page 1, clause 1",
        ),
        ExtractedFieldRead(
            field_name="transaction_type",
            value="purchase",
            confidence=0.93,
            citation="Page 1, clause 2",
        ),
    ]
    checklist_findings = [
        ChecklistFindingRead(
            item_name="buyer_purchase_with_mortgage_requires_lender_evidence",
            status="pass",
            citation="Page 8, clause 14",
            reason="Lender evidence is present",
        )
    ]

    decision = build_review_decision(
        matter_id=UUID("12345678-1234-5678-1234-567812345678"),
        extracted_fields=extracted_fields,
        checklist_findings=checklist_findings,
    )

    assert decision.overall_status == "ready_for_review"
    assert "ready for human review" in decision.review_summary.lower()
    assert "settlement-ready" not in decision.review_summary.lower()
    assert "legal approval" not in decision.review_summary.lower()


def test_build_review_decision_marks_no_evidence_as_insufficient() -> None:
    decision = build_review_decision(
        matter_id=UUID("12345678-1234-5678-1234-567812345678"),
        extracted_fields=[],
        checklist_findings=[],
    )

    assert decision.overall_status == "insufficient_evidence"
    assert "insufficient evidence" in decision.review_summary.lower()
    assert decision.extracted_fields == []
    assert decision.checklist_findings == []
