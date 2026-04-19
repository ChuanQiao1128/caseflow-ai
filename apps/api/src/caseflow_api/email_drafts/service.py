from __future__ import annotations

from uuid import UUID

from caseflow_api.api.schemas import (
    ChecklistFindingRead,
    ExtractedFieldRead,
    FollowUpEmailDraftRead,
    ReviewDecisionRead,
)


def _format_field(field: ExtractedFieldRead) -> str:
    label = field.field_name.replace("_", " ")
    if field.value is None or not str(field.value).strip():
        if field.citation:
            return (
                f"- {label}: not confirmed from the reviewed material (citation: {field.citation})"
            )
        return f"- {label}: not confirmed from the reviewed material"
    if field.citation:
        return f"- {label}: {field.value} (citation: {field.citation})"
    return f"- {label}: {field.value}"


def _format_finding(finding: ChecklistFindingRead) -> str:
    item = finding.item_name.strip()
    parts = [f"- {item}: {finding.status}"]
    if finding.reason:
        parts.append(f"reason: {finding.reason}")
    if finding.citation:
        parts.append(f"citation: {finding.citation}")
    return "; ".join(parts)


def build_email_draft(
    *, matter_id: UUID, review_decision: ReviewDecisionRead
) -> FollowUpEmailDraftRead:
    matter_ref = str(matter_id)
    subject = f"Draft email for matter {matter_ref[:8]}"

    lines: list[str] = [
        "Kia ora,",
        "",
        (
            f"I have prepared a draft note for matter {matter_id} based on the "
            "bounded review findings below."
        ),
        "This is a draft only for human review and should not be treated as final or legal advice.",
        "",
        f"Review summary: {review_decision.review_summary}",
        "",
    ]

    if review_decision.extracted_fields:
        lines.append("Key extracted details:")
        lines.extend(_format_field(field) for field in review_decision.extracted_fields)
        lines.append("")
    else:
        lines.extend(
            [
                "Key extracted details:",
                (
                    "- No reliable extracted details were available, so the draft "
                    "should be treated cautiously."
                ),
                "",
            ]
        )

    if review_decision.checklist_findings:
        lines.append("Checklist issues or uncertainties:")
        lines.extend(_format_finding(finding) for finding in review_decision.checklist_findings)
        lines.append("")
    else:
        lines.extend(
            [
                "Checklist issues or uncertainties:",
                "- No checklist findings were available, so the position remains uncertain.",
                "",
            ]
        )

    if review_decision.overall_status == "insufficient_evidence":
        lines.extend(
            [
                (
                    "Caution: the available evidence is sparse, so this matter may "
                    "need further review and I cannot confirm the position with "
                    "confidence."
                ),
                "Please review the file manually and adjust this draft before any human use.",
            ]
        )
    elif review_decision.overall_status == "ready_for_review":
        lines.extend(
            [
                (
                    "Caution: the review appears to be in a better position, but "
                    "this remains a draft for manual checking."
                ),
                "Please confirm the details against the source material before any human use.",
            ]
        )
    else:
        lines.extend(
            [
                (
                    "Caution: there are unresolved issues or uncertainty, so this "
                    "draft should be edited carefully."
                ),
                "Please confirm the details against the source material before any human use.",
            ]
        )

    body = "\n".join(lines).strip()

    return FollowUpEmailDraftRead(
        matter_id=matter_id,
        subject=subject,
        body=body,
        status="draft_only",
        disclaimer=(
            "This is a draft email only for review before sending. "
            "It does not send anything automatically and is not legal advice or an approval."
        ),
    )
