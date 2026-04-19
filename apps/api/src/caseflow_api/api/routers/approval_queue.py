from __future__ import annotations

from typing import Annotated, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from caseflow_api.api.schemas import ApprovalQueueItemRead
from caseflow_api.approval_queue.service import (
    approve_approval_queue_item,
    create_approval_queue_item,
    list_approval_queue_items,
    reject_approval_queue_item,
)
from caseflow_api.database import get_db

router = APIRouter(tags=["approval-queue"])
DBSession = Annotated[Session, Depends(get_db)]


class ApprovalQueueItemCreateRequest(BaseModel):
    item_type: Literal["follow_up_email_draft"]
    subject: str = Field(min_length=1)
    body: str = Field(min_length=1)
    source_item_id: str = Field(min_length=1)


class ApprovalQueueActionRequest(BaseModel):
    reviewer_notes: str | None = None


@router.post(
    "/organisations/{organisation_id}/matters/{matter_id}/approval-queue",
    response_model=ApprovalQueueItemRead,
    status_code=status.HTTP_201_CREATED,
)
def create_queue_item(
    organisation_id: UUID,
    matter_id: UUID,
    payload: ApprovalQueueItemCreateRequest,
    db: DBSession,
) -> ApprovalQueueItemRead:
    item = create_approval_queue_item(
        db=db,
        organisation_id=organisation_id,
        matter_id=matter_id,
        item_type=payload.item_type,
        subject=payload.subject,
        body=payload.body,
        source_item_id=payload.source_item_id,
    )
    return ApprovalQueueItemRead.model_validate(item)


@router.get(
    "/organisations/{organisation_id}/matters/{matter_id}/approval-queue",
    response_model=list[ApprovalQueueItemRead],
)
def list_queue_items(
    organisation_id: UUID,
    matter_id: UUID,
    db: DBSession,
) -> list[ApprovalQueueItemRead]:
    try:
        items = list_approval_queue_items(
            db=db, organisation_id=organisation_id, matter_id=matter_id
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matter not found",
        ) from exc
    return [ApprovalQueueItemRead.model_validate(item) for item in items]


@router.post(
    "/organisations/{organisation_id}/matters/{matter_id}/approval-queue/{item_id}/approve",
    response_model=ApprovalQueueItemRead,
)
def approve_queue_item(
    organisation_id: UUID,
    matter_id: UUID,
    item_id: UUID,
    payload: ApprovalQueueActionRequest,
    db: DBSession,
) -> ApprovalQueueItemRead:
    try:
        item = approve_approval_queue_item(
            db=db,
            organisation_id=organisation_id,
            matter_id=matter_id,
            item_id=item_id,
            reviewer_notes=payload.reviewer_notes,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matter not found",
        ) from exc
    return ApprovalQueueItemRead.model_validate(item)


@router.post(
    "/organisations/{organisation_id}/matters/{matter_id}/approval-queue/{item_id}/reject",
    response_model=ApprovalQueueItemRead,
)
def reject_queue_item(
    organisation_id: UUID,
    matter_id: UUID,
    item_id: UUID,
    payload: ApprovalQueueActionRequest,
    db: DBSession,
) -> ApprovalQueueItemRead:
    try:
        item = reject_approval_queue_item(
            db=db,
            organisation_id=organisation_id,
            matter_id=matter_id,
            item_id=item_id,
            reviewer_notes=payload.reviewer_notes,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Matter not found",
        ) from exc
    return ApprovalQueueItemRead.model_validate(item)
