from __future__ import annotations

from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import caseflow_api.models  # noqa: F401
from caseflow_api.api.schemas import ReviewDecisionRead
from caseflow_api.approval_queue.service import (
    approve_approval_queue_item,
    create_approval_queue_item,
    list_approval_queue_items,
    reject_approval_queue_item,
)
from caseflow_api.database import Base
from caseflow_api.email_drafts.service import build_email_draft
from caseflow_api.models import Matter, Organisation

ORG_ID = UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
MATTER_ID = UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
OTHER_MATTER_ID = UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")


@pytest.fixture()
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)
        engine.dispose()


@pytest.fixture()
def seeded_matter(db_session):
    organisation = Organisation(id=ORG_ID, name="Approval Law")
    matter = Matter(id=MATTER_ID, organisation_id=ORG_ID, title="Approval Matter", status="open")
    other_matter = Matter(
        id=OTHER_MATTER_ID,
        organisation_id=ORG_ID,
        title="Other Matter",
        status="open",
    )
    db_session.add_all([organisation, matter, other_matter])
    db_session.commit()
    return organisation, matter, other_matter


@pytest.fixture()
def review_decision() -> ReviewDecisionRead:
    return ReviewDecisionRead(
        review_summary="Ready for human review.",
        overall_status="ready_for_review",
    )


def test_create_approval_queue_item_starts_pending_and_lists_by_matter(
    db_session, seeded_matter, review_decision
):
    organisation, matter, other_matter = seeded_matter
    draft = build_email_draft(matter_id=matter.id, review_decision=review_decision)

    item = create_approval_queue_item(
        db=db_session,
        organisation_id=organisation.id,
        matter_id=matter.id,
        item_type="follow_up_email_draft",
        subject=draft.subject,
        body=draft.body,
        source_item_id=str(uuid4()),
    )

    assert item.status == "pending"
    assert item.matter_id == matter.id
    assert item.organisation_id == organisation.id

    items = list_approval_queue_items(
        db=db_session,
        organisation_id=organisation.id,
        matter_id=matter.id,
    )
    assert len(items) == 1
    assert items[0].id == item.id

    other_items = list_approval_queue_items(
        db=db_session,
        organisation_id=organisation.id,
        matter_id=other_matter.id,
    )
    assert other_items == []


def test_approve_and_reject_transitions_update_status_and_notes(
    db_session, seeded_matter, review_decision
):
    organisation, matter, _other_matter = seeded_matter
    draft = build_email_draft(matter_id=matter.id, review_decision=review_decision)
    item = create_approval_queue_item(
        db=db_session,
        organisation_id=organisation.id,
        matter_id=matter.id,
        item_type="follow_up_email_draft",
        subject=draft.subject,
        body=draft.body,
        source_item_id=str(uuid4()),
    )

    approved = approve_approval_queue_item(
        db=db_session,
        organisation_id=organisation.id,
        matter_id=matter.id,
        item_id=item.id,
        reviewer_notes="Approved for sending",
    )
    assert approved.status == "approved"
    assert approved.reviewer_notes == "Approved for sending"

    rejected = reject_approval_queue_item(
        db=db_session,
        organisation_id=organisation.id,
        matter_id=matter.id,
        item_id=item.id,
        reviewer_notes="Needs edits",
    )
    assert rejected.status == "rejected"
    assert rejected.reviewer_notes == "Needs edits"


def test_approval_queue_is_matter_scoped(db_session, seeded_matter, review_decision):
    organisation, matter, other_matter = seeded_matter
    draft = build_email_draft(matter_id=matter.id, review_decision=review_decision)
    item = create_approval_queue_item(
        db=db_session,
        organisation_id=organisation.id,
        matter_id=matter.id,
        item_type="follow_up_email_draft",
        subject=draft.subject,
        body=draft.body,
        source_item_id=str(uuid4()),
    )

    with pytest.raises(ValueError, match="Matter not found"):
        approve_approval_queue_item(
            db=db_session,
            organisation_id=organisation.id,
            matter_id=other_matter.id,
            item_id=item.id,
            reviewer_notes="wrong matter",
        )

    with pytest.raises(ValueError, match="Matter not found"):
        reject_approval_queue_item(
            db=db_session,
            organisation_id=uuid4(),
            matter_id=matter.id,
            item_id=item.id,
            reviewer_notes="wrong org",
        )
