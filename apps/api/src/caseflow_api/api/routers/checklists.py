from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from caseflow_api.api.schemas import ChecklistResponse
from caseflow_api.checklists import evaluate_checklist
from caseflow_api.database import get_db
from caseflow_api.extraction import ExtractionFieldSpec, extract_matter_fields
from caseflow_api.models import Matter

router = APIRouter(tags=["checklists"])
DBSession = Annotated[Session, Depends(get_db)]

CHECKLIST_EXTRACTION_FIELD_SPECS: tuple[ExtractionFieldSpec, ...] = (
    ExtractionFieldSpec(field_name="party_role", query="party role"),
    ExtractionFieldSpec(field_name="transaction_type", query="transaction type"),
    ExtractionFieldSpec(field_name="finance_type", query="finance type"),
    ExtractionFieldSpec(field_name="lender_evidence", query="lender evidence"),
    ExtractionFieldSpec(field_name="discharge_required", query="discharge required"),
    ExtractionFieldSpec(field_name="discharge_evidence", query="discharge evidence"),
)


@router.post(
    "/organisations/{organisation_id}/matters/{matter_id}/checklist",
    response_model=ChecklistResponse,
)
def evaluate_matter_checklist(
    organisation_id: UUID,
    matter_id: UUID,
    db: DBSession,
) -> ChecklistResponse:
    matter_exists = db.scalar(
        select(Matter.id).where(
            Matter.id == matter_id,
            Matter.organisation_id == organisation_id,
        )
    )
    if matter_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matter not found")

    extraction = extract_matter_fields(
        db=db,
        organisation_id=organisation_id,
        matter_id=matter_id,
        field_specs=list(CHECKLIST_EXTRACTION_FIELD_SPECS),
    )
    return evaluate_checklist(matter_id=matter_id, extracted_fields=extraction.extracted_fields)
