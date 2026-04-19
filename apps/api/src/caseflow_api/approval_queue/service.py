from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from caseflow_api.models import ApprovalQueueItem, AuditLog, Matter


def _load_matter(db: Session, *, organisation_id: UUID, matter_id: UUID) -> Matter:
    matter: Matter | None = db.scalar(
        select(Matter).where(
            Matter.id == matter_id,
            Matter.organisation_id == organisation_id,
        )
    )
    if matter is None:
        raise ValueError("Matter not found")
    return matter


def _load_queue_item(
    db: Session, *, organisation_id: UUID, matter_id: UUID, item_id: UUID
) -> ApprovalQueueItem:
    item: ApprovalQueueItem | None = db.scalar(
        select(ApprovalQueueItem).where(
            ApprovalQueueItem.id == item_id,
            ApprovalQueueItem.organisation_id == organisation_id,
            ApprovalQueueItem.matter_id == matter_id,
        )
    )
    if item is None:
        raise ValueError("Matter not found")
    return item


def _add_audit_log(
    db: Session,
    *,
    organisation_id: UUID,
    matter_id: UUID,
    action: str,
    entity_id: str,
    details: dict[str, object],
) -> None:
    db.add(
        AuditLog(
            organisation_id=organisation_id,
            matter_id=matter_id,
            actor_user_id=None,
            action=action,
            entity_type="approval_queue_item",
            entity_id=entity_id,
            details=details,
        )
    )


def create_approval_queue_item(
    *,
    db: Session,
    organisation_id: UUID,
    matter_id: UUID,
    item_type: str,
    subject: str,
    body: str,
    source_item_id: str,
) -> ApprovalQueueItem:
    _load_matter(db, organisation_id=organisation_id, matter_id=matter_id)
    item = ApprovalQueueItem(
        organisation_id=organisation_id,
        matter_id=matter_id,
        item_type=item_type,
        subject=subject,
        body=body,
        source_item_id=source_item_id,
        status="pending",
    )
    db.add(item)
    db.flush()
    _add_audit_log(
        db,
        organisation_id=organisation_id,
        matter_id=matter_id,
        action="approval_queue.created",
        entity_id=str(item.id),
        details={
            "approval_queue_item_id": str(item.id),
            "item_type": item_type,
            "status": "pending",
        },
    )
    db.commit()
    db.refresh(item)
    return item


def list_approval_queue_items(
    *,
    db: Session,
    organisation_id: UUID,
    matter_id: UUID,
) -> list[ApprovalQueueItem]:
    _load_matter(db, organisation_id=organisation_id, matter_id=matter_id)
    statement = (
        select(ApprovalQueueItem)
        .where(
            ApprovalQueueItem.organisation_id == organisation_id,
            ApprovalQueueItem.matter_id == matter_id,
        )
        .order_by(ApprovalQueueItem.created_at)
    )
    return list(db.scalars(statement).all())


def approve_approval_queue_item(
    *,
    db: Session,
    organisation_id: UUID,
    matter_id: UUID,
    item_id: UUID,
    reviewer_notes: str | None = None,
) -> ApprovalQueueItem:
    item = _load_queue_item(
        db,
        organisation_id=organisation_id,
        matter_id=matter_id,
        item_id=item_id,
    )
    item.status = "approved"
    item.reviewer_notes = reviewer_notes
    _add_audit_log(
        db,
        organisation_id=organisation_id,
        matter_id=matter_id,
        action="approval_queue.approved",
        entity_id=str(item.id),
        details={
            "approval_queue_item_id": str(item.id),
            "status": "approved",
            "reviewer_notes": reviewer_notes,
        },
    )
    db.commit()
    db.refresh(item)
    return item


def reject_approval_queue_item(
    *,
    db: Session,
    organisation_id: UUID,
    matter_id: UUID,
    item_id: UUID,
    reviewer_notes: str | None = None,
) -> ApprovalQueueItem:
    item = _load_queue_item(
        db,
        organisation_id=organisation_id,
        matter_id=matter_id,
        item_id=item_id,
    )
    item.status = "rejected"
    item.reviewer_notes = reviewer_notes
    _add_audit_log(
        db,
        organisation_id=organisation_id,
        matter_id=matter_id,
        action="approval_queue.rejected",
        entity_id=str(item.id),
        details={
            "approval_queue_item_id": str(item.id),
            "status": "rejected",
            "reviewer_notes": reviewer_notes,
        },
    )
    db.commit()
    db.refresh(item)
    return item
