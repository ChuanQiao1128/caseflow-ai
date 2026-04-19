from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from uuid import UUID

from caseflow_api.retrieval.vector_search import VectorSearchResult


@dataclass(frozen=True, slots=True)
class EvidenceCitation:
    chunk_id: UUID
    document_id: UUID
    page_number: int | None
    chunk_index: int
    content: str
    score: float
    citation: str


def build_citation(*, document_id: UUID, page_number: int | None, chunk_index: int) -> str:
    page_label = f"page {page_number}" if page_number is not None else "page unknown"
    return f"document {document_id} ({page_label}, chunk {chunk_index})"


def format_evidence_chunks(results: Sequence[VectorSearchResult]) -> list[EvidenceCitation]:
    return [
        EvidenceCitation(
            chunk_id=result.chunk_id,
            document_id=result.document_id,
            page_number=result.page_number,
            chunk_index=result.chunk_index,
            content=result.content,
            score=result.score,
            citation=build_citation(
                document_id=result.document_id,
                page_number=result.page_number,
                chunk_index=result.chunk_index,
            ),
        )
        for result in results
    ]
