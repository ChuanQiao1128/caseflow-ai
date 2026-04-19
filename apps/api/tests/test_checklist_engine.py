from __future__ import annotations

from uuid import UUID

from caseflow_api.api.schemas import ExtractedFieldRead
from caseflow_api.checklists.engine import evaluate_checklist

MATT = UUID("11111111-1111-1111-1111-111111111111")


def test_buyer_purchase_with_mortgage_requires_lender_evidence_passes_when_present() -> None:
    response = evaluate_checklist(
        matter_id=MATT,
        extracted_fields=[
            ExtractedFieldRead(
                field_name="party_role",
                value="buyer",
                confidence=1.0,
                citation="Page 1",
            ),
            ExtractedFieldRead(
                field_name="transaction_type",
                value="purchase",
                confidence=1.0,
                citation="Page 1",
            ),
            ExtractedFieldRead(
                field_name="finance_type",
                value="mortgage",
                confidence=1.0,
                citation="Page 2",
            ),
            ExtractedFieldRead(
                field_name="lender_evidence",
                value="ANZ pre-approval letter",
                confidence=0.9,
                citation="Page 8",
            ),
        ],
    )

    finding = next(
        item
        for item in response.findings
        if item.item_name == "buyer_purchase_with_mortgage_requires_lender_evidence"
    )
    assert finding.status == "pass"
    assert finding.reason == "Lender evidence is present"
    assert finding.citation == "Page 8"


def test_buyer_purchase_with_mortgage_requires_lender_evidence_is_unclear_when_missing() -> None:
    response = evaluate_checklist(
        matter_id=MATT,
        extracted_fields=[
            ExtractedFieldRead(
                field_name="party_role",
                value="buyer",
                confidence=1.0,
                citation="Page 1",
            ),
            ExtractedFieldRead(
                field_name="transaction_type",
                value="purchase",
                confidence=1.0,
                citation="Page 1",
            ),
            ExtractedFieldRead(
                field_name="finance_type",
                value="mortgage",
                confidence=1.0,
                citation="Page 2",
            ),
        ],
    )

    finding = next(
        item
        for item in response.findings
        if item.item_name == "buyer_purchase_with_mortgage_requires_lender_evidence"
    )
    assert finding.status == "unclear"
    assert finding.reason == "Mortgage is indicated, but lender evidence was not found"
    assert finding.citation == "Page 2"


def test_vendor_matter_with_discharge_requires_discharge_evidence() -> None:
    response = evaluate_checklist(
        matter_id=MATT,
        extracted_fields=[
            ExtractedFieldRead(
                field_name="party_role",
                value="vendor",
                confidence=1.0,
                citation="Page 1",
            ),
            ExtractedFieldRead(
                field_name="discharge_required",
                value="yes",
                confidence=1.0,
                citation="Page 4",
            ),
            ExtractedFieldRead(
                field_name="discharge_evidence",
                value="Discharge request lodged with lender",
                confidence=0.95,
                citation="Page 9",
            ),
        ],
    )

    finding = next(
        item
        for item in response.findings
        if item.item_name == "vendor_matter_with_discharge_requires_discharge_evidence"
    )
    assert finding.status == "pass"
    assert finding.reason == "Discharge evidence is present"
    assert finding.citation == "Page 9"
