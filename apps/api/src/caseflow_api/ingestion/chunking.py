from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

SYNTHETIC_DISCLAIMER = "SYNTHETIC DEMO DATA — NOT REAL CLIENT DATA"
PAGE_MARKER_RE = re.compile(r"^--- Page (\d+) ---\s*$", re.MULTILINE)


@dataclass(frozen=True, slots=True)
class SourceTextChunk:
    document_key: str
    page_number: int
    chunk_index: int
    content: str


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(_read_text(path))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return payload


def _extract_pages(content: str) -> list[tuple[int, str]]:
    matches = list(PAGE_MARKER_RE.finditer(content))
    if not matches:
        raise ValueError("source text must contain at least one page marker")

    pages: list[tuple[int, str]] = []
    for index, match in enumerate(matches):
        page_number = int(match.group(1))
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(content)
        page_content = content[start:end].strip()
        if not page_content:
            continue
        pages.append((page_number, page_content))
    return pages


def parse_source_text_file(path: Path) -> list[SourceTextChunk]:
    path = path.expanduser().resolve()
    content = _read_text(path)
    if SYNTHETIC_DISCLAIMER not in content:
        raise ValueError(f"{path.name} missing synthetic disclaimer")

    document_key = path.stem
    chunks: list[SourceTextChunk] = []
    for chunk_index, (page_number, page_content) in enumerate(_extract_pages(content)):
        chunks.append(
            SourceTextChunk(
                document_key=document_key,
                page_number=page_number,
                chunk_index=chunk_index,
                content=page_content,
            )
        )
    return chunks


def load_synthetic_case_summary(case_dir: Path) -> dict[str, Any]:
    case_dir = case_dir.expanduser().resolve()
    matter = _load_json(case_dir / "matter.json")
    documents = _load_json(case_dir / "documents.json")
    document_entries = documents.get("documents")
    if not isinstance(document_entries, list):
        raise ValueError("documents.json must contain documents as a list")

    source_text_dir = case_dir / "source_text"
    document_chunks: list[SourceTextChunk] = []
    for document in document_entries:
        if not isinstance(document, dict):
            raise ValueError("documents.json entries must be objects")
        document_id = document.get("document_id")
        if not isinstance(document_id, str):
            raise ValueError("documents.json entries must contain document_id strings")
        source_text_path = source_text_dir / f"{document_id}.md"
        document_chunks.extend(parse_source_text_file(source_text_path))

    return {
        "matter_title": matter.get("matter_title"),
        "document_count": len(document_entries),
        "page_count": len(document_chunks),
        "chunk_count": len(document_chunks),
    }
