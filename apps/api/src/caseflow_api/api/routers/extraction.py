from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from caseflow_api.api.schemas import MatterExtractionResponse
from caseflow_api.database import get_db
from caseflow_api.extraction import ExtractionFieldSpec, extract_matter_fields
from caseflow_api.models import Matter

router = APIRouter(tags=["extraction"])
DBSession = Annotated[Session, Depends(get_db)]

DEFAULT_EXTRACTION_FIELD_SPECS: tuple[ExtractionFieldSpec, ...] = (
    ExtractionFieldSpec(field_name="settlement_date", query="settlement date"),
    ExtractionFieldSpec(field_name="deposit_amount", query="deposit amount"),
    ExtractionFieldSpec(field_name="party_role", query="party role"),
)


@router.post(
    "/organisations/{organisation_id}/matters/{matter_id}/extract",
    response_model=MatterExtractionResponse,
)
def extract_matter(
    organisation_id: UUID,
    matter_id: UUID,
    db: DBSession,
) -> MatterExtractionResponse:
    matter_exists = db.scalar(
        select(Matter.id).where(
            Matter.id == matter_id,
            Matter.organisation_id == organisation_id,
        )
    )
    if matter_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matter not found")

    return extract_matter_fields(
        db=db,
        organisation_id=organisation_id,
        matter_id=matter_id,
        field_specs=list(DEFAULT_EXTRACTION_FIELD_SPECS),
    )
