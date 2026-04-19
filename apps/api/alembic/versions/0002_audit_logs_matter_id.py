"""Add nullable matter_id to audit_logs.

Revision ID: 0002_audit_logs_matter_id
Revises: 0001_initial
Create Date: 2026-04-19 12:35:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002_audit_logs_matter_id"
down_revision: str | None = "0001_initial"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "audit_logs",
        sa.Column("matter_id", sa.Uuid(), nullable=True),
    )
    op.create_foreign_key(
        "fk_audit_logs_matter_id_matters",
        "audit_logs",
        "matters",
        ["matter_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_audit_logs_matter_id", "audit_logs", ["matter_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_audit_logs_matter_id", table_name="audit_logs")
    op.drop_constraint("fk_audit_logs_matter_id_matters", "audit_logs", type_="foreignkey")
    op.drop_column("audit_logs", "matter_id")
