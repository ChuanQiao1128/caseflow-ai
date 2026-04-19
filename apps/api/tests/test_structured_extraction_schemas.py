from __future__ import annotations

from uuid import UUID

import pytest
from pydantic import ValidationError

from caseflow_api.api.schemas import (
    ChecklistFindingRead,
    ChecklistResponse,
    ExtractedFieldRead,
    MatterExtractionResponse,
)


def test_extracted_field_read_serializes_citation_and_confidence() -> None:
    payload = ExtractedFieldRead(
        field_name="settlement_date",
        value="2026-04-30",
        confidence=0.92,
        citation="Page 3, paragraph 2",
    )

    assert payload.field_name == "settlement_date"
    assert payload.value == "2026-04-30"
    assert payload.confidence == 0.92
    assert payload.citation == "Page 3, paragraph 2"


def test_checklist_finding_read_supports_pass_fail_unclear() -> None:
    passed = ChecklistFindingRead(
        item_name="Finance condition included",
        status="pass",
        citation="Page 5, clause 7",
    )
    failed = ChecklistFindingRead(
        item_name="Deposit amount stated",
        status="fail",
        citation="Page 2, clause 3",
    )
    unclear = ChecklistFindingRead(
        item_name="Settlement date confirmed",
        status="unclear",
        reason="Settlement date not explicitly stated",
        citation="Page 3, clause 4",
    )

    assert passed.status == "pass"
    assert failed.status == "fail"
    assert unclear.status == "unclear"
    assert unclear.reason == "Settlement date not explicitly stated"


def test_checklist_finding_unclear_requires_reason_and_citation() -> None:
    with pytest.raises(ValidationError):
        ChecklistFindingRead(
            item_name="Settlement date confirmed",
            status="unclear",
            citation="Page 3, clause 4",
        )


def test_matter_extraction_response_groups_fields() -> None:
    payload = MatterExtractionResponse(
        matter_id=UUID("12345678-1234-5678-1234-567812345678"),
        extracted_fields=[
            ExtractedFieldRead(
                field_name="settlement_date",
                value="2026-04-30",
                confidence=0.92,
                citation="Page 3, paragraph 2",
            )
        ],
    )

    assert payload.extracted_fields[0].field_name == "settlement_date"


def test_checklist_response_groups_findings() -> None:
    payload = ChecklistResponse(
        matter_id=UUID("12345678-1234-5678-1234-567812345678"),
        findings=[
            ChecklistFindingRead(
                item_name="Finance condition included",
                status="pass",
                citation="Page 5, clause 7",
            )
        ],
    )

    assert payload.findings[0].status == "pass"
