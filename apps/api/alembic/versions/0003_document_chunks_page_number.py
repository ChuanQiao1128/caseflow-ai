"""Add page_number to document_chunks.

Revision ID: 0003_document_chunks_page_number
Revises: 0002_audit_logs_matter_id
Create Date: 2026-04-19 13:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0003_document_chunks_page_number"
down_revision: str | None = "0002_audit_logs_matter_id"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "document_chunks",
        sa.Column("page_number", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("document_chunks", "page_number")
