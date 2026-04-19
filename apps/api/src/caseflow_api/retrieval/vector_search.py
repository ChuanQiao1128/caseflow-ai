from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from caseflow_api.models import Document, DocumentChunk, Matter


@dataclass(frozen=True, slots=True)
class VectorSearchResult:
    chunk_id: UUID
    document_id: UUID
    page_number: int | None
    chunk_index: int
    content: str
    score: float


def search_document_chunks(
    *,
    db: Session,
    organisation_id: UUID,
    matter_id: UUID,
    query_embedding: list[float],
    limit: int = 5,
) -> list[VectorSearchResult]:
    matter_exists = db.scalar(
        select(Matter.id).where(
            Matter.id == matter_id,
            Matter.organisation_id == organisation_id,
        )
    )
    if matter_exists is None:
        raise ValueError("Matter not found for organisation")

    distance_expr = DocumentChunk.embedding.cosine_distance(query_embedding)
    statement = (
        select(
            DocumentChunk.id,
            DocumentChunk.document_id,
            DocumentChunk.page_number,
            DocumentChunk.chunk_index,
            DocumentChunk.content,
            distance_expr.label("score"),
        )
        .join(Document, Document.id == DocumentChunk.document_id)
        .join(Matter, Matter.id == Document.matter_id)
        .where(
            Matter.id == matter_id,
            Matter.organisation_id == organisation_id,
            DocumentChunk.embedding.is_not(None),
        )
        .order_by(distance_expr.asc(), DocumentChunk.chunk_index.asc())
        .limit(limit)
    )

    rows = db.execute(statement).all()
    return [
        VectorSearchResult(
            chunk_id=row.id,
            document_id=row.document_id,
            page_number=row.page_number,
            chunk_index=row.chunk_index,
            content=row.content,
            score=float(row.score),
        )
        for row in rows
    ]
