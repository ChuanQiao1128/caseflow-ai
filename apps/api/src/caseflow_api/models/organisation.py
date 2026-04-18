from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from caseflow_api.database import Base
from caseflow_api.models.base import TimestampMixin, UUIDPrimaryKeyMixin

if TYPE_CHECKING:
    from caseflow_api.models.audit_log import AuditLog
    from caseflow_api.models.matter import Matter
    from caseflow_api.models.user import User


class Organisation(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "organisations"

    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

    users: Mapped[list[User]] = relationship(
        back_populates="organisation",
        cascade="all, delete-orphan",
    )
    matters: Mapped[list[Matter]] = relationship(
        back_populates="organisation",
        cascade="all, delete-orphan",
    )
    audit_logs: Mapped[list[AuditLog]] = relationship(
        back_populates="organisation",
        cascade="all, delete-orphan",
    )
