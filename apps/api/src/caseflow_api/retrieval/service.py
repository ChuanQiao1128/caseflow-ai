from __future__ import annotations

from dataclasses import dataclass
from typing import Final
from uuid import UUID

from sqlalchemy.orm import Session

from caseflow_api.ai.embeddings import embed_query
from caseflow_api.retrieval.evidence import EvidenceCitation, format_evidence_chunks
from caseflow_api.retrieval.vector_search import search_document_chunks

DEFAULT_RETRIEVAL_LIMIT: Final[int] = 5
DEFAULT_MAX_DISTANCE: Final[float] = 0.95


@dataclass(frozen=True, slots=True)
class MatterRetrievalResult:
    organisation_id: UUID
    matter_id: UUID
    query: str
    confidence: str
    has_evidence: bool
    results: list[EvidenceCitation]
    message: str | None = None


def search_matter_evidence(
    *,
    db: Session,
    organisation_id: UUID,
    matter_id: UUID,
    query: str,
    limit: int = DEFAULT_RETRIEVAL_LIMIT,
    max_distance: float = DEFAULT_MAX_DISTANCE,
) -> MatterRetrievalResult:
    query_embedding = embed_query(query)
    rows = search_document_chunks(
        db=db,
        organisation_id=organisation_id,
        matter_id=matter_id,
        query_embedding=query_embedding,
        limit=limit,
    )
    filtered_rows = [row for row in rows if row.score <= max_distance]
    evidence = format_evidence_chunks(filtered_rows)
    if not evidence:
        return MatterRetrievalResult(
            organisation_id=organisation_id,
            matter_id=matter_id,
            query=query,
            confidence="low",
            has_evidence=False,
            results=[],
            message="No relevant evidence found",
        )

    return MatterRetrievalResult(
        organisation_id=organisation_id,
        matter_id=matter_id,
        query=query,
        confidence="high",
        has_evidence=True,
        results=evidence,
        message=None,
    )
