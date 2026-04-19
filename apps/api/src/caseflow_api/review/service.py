from __future__ import annotations

from collections.abc import Iterable
from typing import Literal
from uuid import UUID

from caseflow_api.api.schemas import (
    ChecklistFindingRead,
    ExtractedFieldRead,
    ReviewDecisionRead,
)

_BOUNDARY_DISCLAIMER = (
    "This review is a bounded human review aid, not legal advice or a legal approval. "
    "It highlights extracted evidence and checklist findings for manual review."
)


def _has_evidence(items: Iterable[ExtractedFieldRead]) -> bool:
    return any(item.value is not None and str(item.value).strip() for item in items)


def _format_extracted_field(field: ExtractedFieldRead) -> str:
    if field.value is None or not str(field.value).strip():
        return f"- {field.field_name}: no extracted value (citation: {field.citation})"
    return f"- {field.field_name}: {field.value} (citation: {field.citation})"


def _format_checklist_finding(finding: ChecklistFindingRead) -> str:
    citation = finding.citation or "needs_human_review"
    reason = f" — {finding.reason}" if finding.reason else ""
    return f"- {finding.item_name}: {finding.status}{reason} (citation: {citation})"


def _overall_status(
    *,
    extracted_fields: list[ExtractedFieldRead],
    checklist_findings: list[ChecklistFindingRead],
) -> str:
    if not extracted_fields and not checklist_findings:
        return "insufficient_evidence"

    if not _has_evidence(extracted_fields):
        return "insufficient_evidence"

    if checklist_findings and all(finding.status == "pass" for finding in checklist_findings):
        return "ready_for_review"

    return "needs_human_review"


def _summary_for_status(overall_status: str) -> str:
    if overall_status == "insufficient_evidence":
        return (
            "Insufficient evidence is available for a bounded human review. "
            "More matter-specific evidence is needed before any manual review can be supported."
        )
    if overall_status == "ready_for_review":
        return (
            "Ready for human review: the evidence appears sufficient for a bounded review. "
            "The extracted fields and checklist findings are matter-scoped and citation-backed, "
            "but this is not legal advice and does not make a final legal conclusion."
        )
    return (
        "Human review recommended because the extracted fields or checklist findings remain "
        "incomplete, unclear, or mixed. This summary is matter-scoped, citation-backed where "
        "evidence exists, and not legal advice."
    )


def build_review_decision(
    *,
    matter_id: UUID,
    extracted_fields: list[ExtractedFieldRead],
    checklist_findings: list[ChecklistFindingRead],
) -> ReviewDecisionRead:
    overall_status = _overall_status(
        extracted_fields=extracted_fields,
        checklist_findings=checklist_findings,
    )

    sections: list[str] = [
        _summary_for_status(overall_status),
        f"Matter {matter_id} review context:",
    ]

    if extracted_fields:
        sections.append("Extracted fields:")
        sections.extend(_format_extracted_field(field) for field in extracted_fields)
    else:
        sections.append("Extracted fields: none available.")

    if checklist_findings:
        sections.append("Checklist findings:")
        sections.extend(_format_checklist_finding(finding) for finding in checklist_findings)
    else:
        sections.append("Checklist findings: none available.")

    review_summary = "\n".join(sections)

    if overall_status == "insufficient_evidence":
        status: Literal["needs_human_review", "ready_for_review", "insufficient_evidence"] = (
            "insufficient_evidence"
        )
    elif overall_status == "ready_for_review":
        status = "ready_for_review"
    else:
        status = "needs_human_review"

    return ReviewDecisionRead(
        review_summary=review_summary,
        overall_status=status,
        extracted_fields=extracted_fields,
        checklist_findings=checklist_findings,
    )
