from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from caseflow_api.database import Base
from caseflow_api.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from caseflow_api.models.matter import Matter
    from caseflow_api.models.organisation import Organisation


class ApprovalQueueItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "approval_queue_items"

    organisation_id: Mapped[UUID] = mapped_column(
        ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False, index=True
    )
    matter_id: Mapped[UUID] = mapped_column(
        ForeignKey("matters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    item_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    source_item_id: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(40), default="pending", nullable=False, index=True)
    reviewer_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    organisation: Mapped[Organisation] = relationship()
    matter: Mapped[Matter] = relationship(back_populates="approval_queue_items")
