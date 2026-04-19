from __future__ import annotations

import inspect
import os
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from caseflow_api.ai.embeddings import EMBEDDING_DIMENSION, embed_text
from caseflow_api.database import Base
from caseflow_api.ingestion.chunking import parse_source_text_file
from caseflow_api.ingestion.synthetic_ingestion import prepare_synthetic_chunk_records
from caseflow_api.models import Document, DocumentChunk, Matter, Organisation
from caseflow_api.retrieval import (
    build_citation,
    format_evidence_chunks,
    search_document_chunks,
)
from caseflow_api.retrieval.service import search_matter_evidence

REPO_ROOT = Path(__file__).resolve().parents[3]
CASE_DIR = (
    REPO_ROOT / "synthetic-data" / "property-settlement" / "case-001-individual-buyer-mortgage"
)
CASEFLOW_TEST_DATABASE_URL = os.getenv("CASEFLOW_TEST_DATABASE_URL")


def test_embed_text_is_deterministic() -> None:
    text_value = "Finance condition due 30 April 2026"

    first = embed_text(text_value)
    second = embed_text(text_value)

    assert first == second


def test_embed_text_returns_1536_float_values() -> None:
    vector = embed_text("Synthetic settlement note")

    assert len(vector) == EMBEDDING_DIMENSION
    assert all(isinstance(value, float) for value in vector)
    assert any(value != 0.0 for value in vector)


def test_synthetic_source_text_chunks_can_be_embedded() -> None:
    source_text_file = CASE_DIR / "source_text" / "doc-001.md"

    chunks = parse_source_text_file(source_text_file)
    embeddings = [embed_text(chunk.content) for chunk in chunks]

    assert len(embeddings) == len(chunks)
    assert all(len(vector) == EMBEDDING_DIMENSION for vector in embeddings)
    assert all(isinstance(value, float) for vector in embeddings for value in vector)


def test_prepare_synthetic_chunk_records_uses_local_embeddings() -> None:
    document_lookup = {
        "doc-001": uuid4(),
        "doc-002": uuid4(),
        "doc-003": uuid4(),
        "doc-004": uuid4(),
        "doc-005": uuid4(),
    }

    records = prepare_synthetic_chunk_records(CASE_DIR, document_lookup=document_lookup)

    assert records
    assert all(
        record.embedding is not None and len(record.embedding) == EMBEDDING_DIMENSION
        for record in records
    )
    assert all(isinstance(value, float) for record in records for value in record.embedding)
    assert {record.page_number for record in records} == {1, 2, 3}


def test_vector_search_requires_organisation_and_matter_ids() -> None:
    signature = inspect.signature(search_document_chunks)

    assert "organisation_id" in signature.parameters
    assert "matter_id" in signature.parameters
    assert signature.parameters["organisation_id"].kind is inspect.Parameter.KEYWORD_ONLY
    assert signature.parameters["matter_id"].kind is inspect.Parameter.KEYWORD_ONLY


@pytest.mark.skipif(
    not os.getenv("CASEFLOW_TEST_DATABASE_URL"),
    reason="CASEFLOW_TEST_DATABASE_URL is required for pgvector integration testing",
)
def test_vector_search_stays_within_matter_scope() -> None:
    database_url = os.environ["CASEFLOW_TEST_DATABASE_URL"]
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    with engine.begin() as connection:
        connection.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        Base.metadata.create_all(bind=connection)

    session = SessionLocal()
    try:
        organisation = Organisation(name=f"Org {uuid4()}")
        matter_a = Matter(title="Matter A", organisation=organisation)
        matter_b = Matter(title="Matter B", organisation=organisation)
        session.add_all([organisation, matter_a, matter_b])
        session.flush()

        doc_a = Document(
            matter_id=matter_a.id,
            filename="doc-a.pdf",
            mime_type="application/pdf",
            storage_key="case-a/doc-a.pdf",
        )
        doc_b = Document(
            matter_id=matter_b.id,
            filename="doc-b.pdf",
            mime_type="application/pdf",
            storage_key="case-b/doc-b.pdf",
        )
        session.add_all([doc_a, doc_b])
        session.flush()

        chunk_a = DocumentChunk(
            document_id=doc_a.id,
            chunk_index=0,
            page_number=1,
            content="Buyer must satisfy finance condition by 30 April 2026.",
            embedding=embed_text("Buyer must satisfy finance condition by 30 April 2026."),
        )
        chunk_b = DocumentChunk(
            document_id=doc_b.id,
            chunk_index=0,
            page_number=1,
            content="Vendor must discharge the mortgage before settlement.",
            embedding=embed_text("Vendor must discharge the mortgage before settlement."),
        )
        session.add_all([chunk_a, chunk_b])
        session.commit()

        results = search_document_chunks(
            db=session,
            organisation_id=organisation.id,
            matter_id=matter_a.id,
            query_embedding=embed_text("Vendor must discharge the mortgage before settlement."),
            limit=5,
        )

        assert results
        assert all(result.document_id == doc_a.id for result in results)
        assert all(result.chunk_id == chunk_a.id for result in results)
        assert all(result.page_number == 1 for result in results)
        assert all(result.chunk_index == 0 for result in results)
    finally:
        session.close()
        with engine.begin() as connection:
            Base.metadata.drop_all(bind=connection)


def test_evidence_formatting_includes_citation_fields() -> None:
    result = type(
        "Result",
        (),
        {
            "chunk_id": uuid4(),
            "document_id": uuid4(),
            "page_number": 2,
            "chunk_index": 3,
            "content": "Sample evidence",
            "score": 0.123,
        },
    )()
    formatted = format_evidence_chunks([result])

    assert formatted[0].chunk_id == result.chunk_id
    assert formatted[0].document_id == result.document_id
    assert formatted[0].page_number == 2
    assert formatted[0].chunk_index == 3
    assert formatted[0].citation == build_citation(
        document_id=result.document_id,
        page_number=2,
        chunk_index=3,
    )


def test_search_service_returns_low_confidence_when_no_relevant_evidence(
    db_session,
) -> None:
    organisation = Organisation(name="Org")
    matter = Matter(title="Matter", organisation=organisation)
    document = Document(
        matter=matter,
        filename="doc.pdf",
        mime_type="application/pdf",
        storage_key="storage/doc.pdf",
    )
    db_session.add_all([organisation, matter, document])
    db_session.flush()
    db_session.add(
        DocumentChunk(
            document_id=document.id,
            chunk_index=0,
            page_number=1,
            content="Completely unrelated text.",
            embedding=embed_text("Completely unrelated text."),
        )
    )
    db_session.commit()

    retrieval = search_matter_evidence(
        db=db_session,
        organisation_id=organisation.id,
        matter_id=matter.id,
        query="qwerty zxcvbnm unrelated nonsense",
        limit=5,
        max_distance=0.0,
    )

    assert retrieval.has_evidence is False
    assert retrieval.confidence == "low"
    assert retrieval.results == []
    assert retrieval.message == "No relevant evidence found"
