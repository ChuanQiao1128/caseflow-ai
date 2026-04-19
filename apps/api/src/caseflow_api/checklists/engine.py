from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from caseflow_api.api.schemas import ChecklistFindingRead, ChecklistResponse, ExtractedFieldRead


@dataclass(frozen=True, slots=True)
class ChecklistRule:
    item_name: str
    applies: callable
    evidence_field: str
    reason_present: str
    reason_missing: str
    fallback_citation: str = "needs_human_review"


def _normalize(value: str | None) -> str:
    return value.strip().lower() if value else ""


def _field_map(extracted_fields: list[ExtractedFieldRead]) -> dict[str, ExtractedFieldRead]:
    return {field.field_name: field for field in extracted_fields}


def _has_truthy_indicator(value: str | None) -> bool:
    return _normalize(value) in {"yes", "true", "required", "y", "1", "present"}


def _is_buyer_purchase_with_mortgage(fields: dict[str, ExtractedFieldRead]) -> bool:
    return (
        _normalize(fields.get("party_role").value if fields.get("party_role") else None) == "buyer"
        and _normalize(fields.get("transaction_type").value if fields.get("transaction_type") else None)
        == "purchase"
        and _normalize(fields.get("finance_type").value if fields.get("finance_type") else None)
        == "mortgage"
    )


def _is_vendor_matter_with_discharge(fields: dict[str, ExtractedFieldRead]) -> bool:
    return (
        _normalize(fields.get("party_role").value if fields.get("party_role") else None) == "vendor"
        and _has_truthy_indicator(
            fields.get("discharge_required").value if fields.get("discharge_required") else None
        )
    )


RULES: tuple[ChecklistRule, ...] = (
    ChecklistRule(
        item_name="buyer_purchase_with_mortgage_requires_lender_evidence",
        applies=_is_buyer_purchase_with_mortgage,
        evidence_field="lender_evidence",
        reason_present="Lender evidence is present",
        reason_missing="Mortgage is indicated, but lender evidence was not found",
    ),
    ChecklistRule(
        item_name="vendor_matter_with_discharge_requires_discharge_evidence",
        applies=_is_vendor_matter_with_discharge,
        evidence_field="discharge_evidence",
        reason_present="Discharge evidence is present",
        reason_missing="Discharge is required, but discharge evidence was not found",
    ),
)


def _finding_from_rule(rule: ChecklistRule, fields: dict[str, ExtractedFieldRead]) -> ChecklistFindingRead:
    evidence = fields.get(rule.evidence_field)
    if evidence and evidence.value and evidence.value.strip():
        return ChecklistFindingRead(
            item_name=rule.item_name,
            status="pass",
            citation=evidence.citation,
            reason=rule.reason_present,
        )

    cited_field = fields.get("finance_type") or fields.get("discharge_required") or fields.get("party_role")
    citation = cited_field.citation if cited_field else rule.fallback_citation
    return ChecklistFindingRead(
        item_name=rule.item_name,
        status="unclear",
        citation=citation,
        reason=rule.reason_missing,
    )


def evaluate_checklist(*, matter_id: UUID, extracted_fields: list[ExtractedFieldRead]) -> ChecklistResponse:
    fields = _field_map(extracted_fields)
    findings: list[ChecklistFindingRead] = []

    for rule in RULES:
        if rule.applies(fields):
            findings.append(_finding_from_rule(rule, fields))

    return ChecklistResponse(matter_id=matter_id, findings=findings)
