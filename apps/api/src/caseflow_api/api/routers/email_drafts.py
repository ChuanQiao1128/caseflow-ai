from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from caseflow_api.api.routers.checklists import CHECKLIST_EXTRACTION_FIELD_SPECS
from caseflow_api.api.schemas import FollowUpEmailDraftRead
from caseflow_api.checklists import evaluate_checklist
from caseflow_api.database import get_db
from caseflow_api.email_drafts.service import build_email_draft
from caseflow_api.extraction import extract_matter_fields
from caseflow_api.models import Matter
from caseflow_api.review.service import build_review_decision

router = APIRouter(tags=["email-drafts"])
DBSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/organisations/{organisation_id}/matters/{matter_id}/email-draft",
    response_model=FollowUpEmailDraftRead,
)
def create_email_draft(
    organisation_id: UUID,
    matter_id: UUID,
    db: DBSession,
) -> FollowUpEmailDraftRead:
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
    checklist = evaluate_checklist(
        matter_id=matter_id,
        extracted_fields=extraction.extracted_fields,
    )
    review_decision = build_review_decision(
        matter_id=matter_id,
        extracted_fields=extraction.extracted_fields,
        checklist_findings=checklist.findings,
    )
    return build_email_draft(matter_id=matter_id, review_decision=review_decision)
