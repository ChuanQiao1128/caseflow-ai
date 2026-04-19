from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from caseflow_api.api.schemas import (
    EvidenceChunkRead,
    MatterSearchRequest,
    MatterSearchResponse,
)
from caseflow_api.database import get_db
from caseflow_api.models import Matter
from caseflow_api.retrieval import search_matter_evidence

router = APIRouter(tags=["retrieval"])
DBSession = Annotated[Session, Depends(get_db)]


@router.post(
    "/organisations/{organisation_id}/matters/{matter_id}/search",
    response_model=MatterSearchResponse,
)
def search_matter(
    organisation_id: UUID,
    matter_id: UUID,
    payload: MatterSearchRequest,
    db: DBSession,
) -> MatterSearchResponse:
    matter_exists = db.scalar(
        select(Matter.id).where(
            Matter.id == matter_id,
            Matter.organisation_id == organisation_id,
        )
    )
    if matter_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matter not found")

    retrieval = search_matter_evidence(
        db=db,
        organisation_id=organisation_id,
        matter_id=matter_id,
        query=payload.query,
        limit=payload.limit,
    )

    return MatterSearchResponse(
        organisation_id=retrieval.organisation_id,
        matter_id=retrieval.matter_id,
        query=retrieval.query,
        results=[EvidenceChunkRead.model_validate(item) for item in retrieval.results],
        confidence=retrieval.confidence,
        has_evidence=retrieval.has_evidence,
        message=retrieval.message,
    )
