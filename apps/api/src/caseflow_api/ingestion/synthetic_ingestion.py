from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from caseflow_api.ai.embeddings import embed_text
from caseflow_api.ingestion.chunking import parse_source_text_file
from caseflow_api.models import Document, DocumentChunk, Matter


@dataclass(frozen=True, slots=True)
class PreparedChunkRecord:
    document_id: UUID
    chunk_index: int
    page_number: int | None
    content: str
    embedding: list[float]


@dataclass(frozen=True, slots=True)
class SyntheticDocumentMatch:
    document_id: UUID
    document_key: str
    filename: str
    storage_key: str


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return payload


def _case_documents(case_dir: Path) -> list[dict[str, Any]]:
    payload = _load_json(case_dir / "documents.json")
    documents = payload.get("documents")
    if not isinstance(documents, list):
        raise ValueError("documents.json must contain documents as a list")
    result: list[dict[str, Any]] = []
    for document in documents:
        if not isinstance(document, dict):
            raise ValueError("documents.json entries must be objects")
        result.append(document)
    return result


def _normalize_lookup_key(value: str) -> str:
    return value.strip().lower()


def _build_document_aliases(document: Document) -> set[str]:
    return {
        _normalize_lookup_key(document.storage_key),
        _normalize_lookup_key(document.filename),
        _normalize_lookup_key(Path(document.storage_key).name),
        _normalize_lookup_key(Path(document.filename).stem),
    }


def load_synthetic_case_documents(
    db: Session,
    *,
    organisation_id: UUID,
    matter_id: UUID,
    case_dir: Path,
) -> list[SyntheticDocumentMatch]:
    matter = db.scalar(
        select(Matter).where(
            Matter.id == matter_id,
            Matter.organisation_id == organisation_id,
        )
    )
    if matter is None:
        raise ValueError("Matter not found for organisation")

    documents = list(
        db.scalars(
            select(Document)
            .join(Matter)
            .where(
                Matter.id == matter_id,
                Matter.organisation_id == organisation_id,
            )
        ).all()
    )
    if not documents:
        raise ValueError("No documents registered for matter")

    document_rows = _case_documents(case_dir)
    by_alias: dict[str, Document] = {}
    for document in documents:
        for alias in _build_document_aliases(document):
            by_alias.setdefault(alias, document)

    matches: list[SyntheticDocumentMatch] = []
    for document_row in document_rows:
        document_id = str(document_row.get("document_id", "")).strip()
        filename = str(document_row.get("filename", "")).strip()
        storage_key = str(document_row.get("storage_key", "")).strip()
        key_candidates = [
            document_id,
            filename,
            storage_key,
            Path(filename).stem if filename else "",
            Path(storage_key).name if storage_key else "",
            f"{document_id}.pdf" if document_id else "",
            f"{document_id}.md" if document_id else "",
        ]
        matched_document = None
        for candidate in key_candidates:
            if not candidate:
                continue
            alias = _normalize_lookup_key(candidate)
            if alias in by_alias:
                matched_document = by_alias[alias]
                break
        if matched_document is None:
            identifier = document_id or filename or storage_key
            raise ValueError(
                f"Could not match synthetic document {identifier!r} to matter documents"
            )
        matches.append(
            SyntheticDocumentMatch(
                document_id=matched_document.id,
                document_key=document_id or Path(filename).stem,
                filename=matched_document.filename,
                storage_key=matched_document.storage_key,
            )
        )
    return matches


def prepare_synthetic_chunk_records(
    case_dir: Path,
    *,
    document_lookup: dict[str, UUID],
) -> list[PreparedChunkRecord]:
    case_dir = case_dir.expanduser().resolve()
    source_text_dir = case_dir / "source_text"
    if not source_text_dir.is_dir():
        raise FileNotFoundError(f"Missing source_text directory: {source_text_dir}")

    records: list[PreparedChunkRecord] = []
    for source_text_file in sorted(source_text_dir.glob("*.md")):
        document_key = source_text_file.stem
        document_id = document_lookup.get(document_key)
        if document_id is None:
            raise ValueError(
                f"No document mapping found for source text file {source_text_file.name}"
            )

        for chunk in parse_source_text_file(source_text_file):
            records.append(
                PreparedChunkRecord(
                    document_id=document_id,
                    chunk_index=chunk.chunk_index,
                    page_number=chunk.page_number,
                    content=chunk.content,
                    embedding=embed_text(chunk.content),
                )
            )
    return records


def ingest_synthetic_case_chunks(
    db: Session,
    *,
    organisation_id: UUID,
    matter_id: UUID,
    case_dir: Path,
) -> list[DocumentChunk]:
    matches = load_synthetic_case_documents(
        db,
        organisation_id=organisation_id,
        matter_id=matter_id,
        case_dir=case_dir,
    )
    document_lookup = {match.document_key: match.document_id for match in matches}
    records = prepare_synthetic_chunk_records(case_dir, document_lookup=document_lookup)

    chunks: list[DocumentChunk] = []
    for record in records:
        chunk = DocumentChunk(
            document_id=record.document_id,
            chunk_index=record.chunk_index,
            page_number=record.page_number,
            content=record.content,
            embedding=record.embedding,
        )
        db.add(chunk)
        chunks.append(chunk)

    db.commit()
    for chunk in chunks:
        db.refresh(chunk)
    return chunks
