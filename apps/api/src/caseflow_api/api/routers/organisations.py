from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from caseflow_api.api.schemas import (
    AuditLogRead,
    DocumentCreate,
    DocumentRead,
    MatterCreate,
    MatterRead,
    OrganisationCreate,
    OrganisationRead,
)
from caseflow_api.database import get_db
from caseflow_api.models import AuditLog, Document, Matter, Organisation

router = APIRouter(tags=["organisations"])
DBSession = Annotated[Session, Depends(get_db)]


@router.post("/organisations", response_model=OrganisationRead, status_code=status.HTTP_201_CREATED)
def create_organisation(payload: OrganisationCreate, db: DBSession) -> Organisation:
    organisation = Organisation(name=payload.name)
    db.add(organisation)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organisation name already exists",
        ) from exc
    db.refresh(organisation)
    return organisation


@router.get("/organisations/{organisation_id}", response_model=OrganisationRead)
def read_organisation(organisation_id: UUID, db: DBSession) -> Organisation:
    organisation = db.get(Organisation, organisation_id)
    if organisation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found")
    return organisation


@router.post(
    "/organisations/{organisation_id}/matters",
    response_model=MatterRead,
    status_code=status.HTTP_201_CREATED,
)
def create_matter(organisation_id: UUID, payload: MatterCreate, db: DBSession) -> Matter:
    organisation = db.get(Organisation, organisation_id)
    if organisation is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organisation not found")

    matter = Matter(
        organisation_id=organisation_id,
        reference=payload.reference,
        title=payload.title,
    )
    db.add(matter)
    db.flush()
    db.add(
        AuditLog(
            organisation_id=organisation_id,
            matter_id=matter.id,
            actor_user_id=None,
            action="matter.created",
            entity_type="matter",
            entity_id=str(matter.id),
            details={"matter_id": str(matter.id), "title": matter.title},
        )
    )
    db.commit()
    db.refresh(matter)
    return matter


@router.get("/organisations/{organisation_id}/matters", response_model=list[MatterRead])
def list_matters(organisation_id: UUID, db: DBSession) -> list[Matter]:
    statement = (
        select(Matter).where(Matter.organisation_id == organisation_id).order_by(Matter.created_at)
    )
    return list(db.scalars(statement).all())


@router.get("/organisations/{organisation_id}/matters/{matter_id}", response_model=MatterRead)
def read_matter(organisation_id: UUID, matter_id: UUID, db: DBSession) -> Matter:
    statement = select(Matter).where(
        Matter.id == matter_id,
        Matter.organisation_id == organisation_id,
    )
    matter = db.scalar(statement)
    if matter is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matter not found")
    return matter


@router.post(
    "/organisations/{organisation_id}/matters/{matter_id}/documents",
    response_model=DocumentRead,
    status_code=status.HTTP_201_CREATED,
)
def create_document(
    organisation_id: UUID,
    matter_id: UUID,
    payload: DocumentCreate,
    db: DBSession,
) -> Document:
    matter = db.scalar(
        select(Matter).where(
            Matter.id == matter_id,
            Matter.organisation_id == organisation_id,
        )
    )
    if matter is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matter not found")

    document = Document(
        matter_id=matter_id,
        filename=payload.filename,
        mime_type=payload.mime_type,
        storage_key=payload.storage_key,
    )
    db.add(document)
    db.flush()
    db.add(
        AuditLog(
            organisation_id=organisation_id,
            matter_id=matter.id,
            actor_user_id=None,
            action="document.registered",
            entity_type="document",
            entity_id=str(document.id),
            details={
                "document_id": str(document.id),
                "matter_id": str(matter.id),
                "filename": document.filename,
            },
        )
    )
    db.commit()
    db.refresh(document)
    return document


@router.get(
    "/organisations/{organisation_id}/matters/{matter_id}/documents",
    response_model=list[DocumentRead],
)
def list_documents(organisation_id: UUID, matter_id: UUID, db: DBSession) -> list[Document]:
    statement = (
        select(Document)
        .join(Matter)
        .where(
            Matter.id == matter_id,
            Matter.organisation_id == organisation_id,
        )
        .order_by(Document.created_at)
    )
    return list(db.scalars(statement).all())


@router.get(
    "/organisations/{organisation_id}/matters/{matter_id}/audit-logs",
    response_model=list[AuditLogRead],
)
def list_audit_logs(organisation_id: UUID, matter_id: UUID, db: DBSession) -> list[AuditLog]:
    matter_exists = db.scalar(
        select(Matter.id).where(
            Matter.id == matter_id,
            Matter.organisation_id == organisation_id,
        )
    )
    if matter_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Matter not found")

    statement = (
        select(AuditLog)
        .where(
            AuditLog.organisation_id == organisation_id,
            AuditLog.matter_id == matter_id,
        )
        .order_by(AuditLog.created_at)
    )
    return list(db.scalars(statement).all())
