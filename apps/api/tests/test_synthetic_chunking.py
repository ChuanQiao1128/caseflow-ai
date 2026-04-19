from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from caseflow_api.ingestion.chunking import parse_source_text_file

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = REPO_ROOT / "synthetic-data" / "property-settlement"
CASE_IDS = [
    "case-001-individual-buyer-mortgage",
    "case-002-individual-vendor-discharge",
    "case-003-trust-buyer-mortgage-cdd",
    "case-004-trust-vendor-deed-variation",
]
DISCLAIMER = "SYNTHETIC DEMO DATA — NOT REAL CLIENT DATA"
SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "preview_synthetic_chunks.py"
SCRIPT_SPEC = importlib.util.spec_from_file_location("preview_synthetic_chunks", SCRIPT_PATH)
assert SCRIPT_SPEC is not None and SCRIPT_SPEC.loader is not None
SCRIPT_MODULE = importlib.util.module_from_spec(SCRIPT_SPEC)
SCRIPT_SPEC.loader.exec_module(SCRIPT_MODULE)
main = SCRIPT_MODULE.main


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_source_text_exists_for_each_document(case_id: str) -> None:
    case_dir = DATA_ROOT / case_id
    documents = json.loads((case_dir / "documents.json").read_text(encoding="utf-8"))["documents"]
    source_text_dir = case_dir / "source_text"

    assert source_text_dir.is_dir()
    for document in documents:
        assert (source_text_dir / f"{document['document_id']}.md").is_file()


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_source_text_files_contain_disclaimer(case_id: str) -> None:
    case_dir = DATA_ROOT / case_id
    source_text_dir = case_dir / "source_text"

    for source_text_file in source_text_dir.glob("*.md"):
        assert DISCLAIMER in source_text_file.read_text(encoding="utf-8")


def test_chunk_parser_extracts_page_numbers_and_content() -> None:
    source_text_file = (
        DATA_ROOT
        / "case-001-individual-buyer-mortgage"
        / "source_text"
        / "doc-001.md"
    )

    chunks = parse_source_text_file(source_text_file)

    assert [chunk.page_number for chunk in chunks] == [1, 2, 3]
    assert all(chunk.content.strip() for chunk in chunks)
    assert chunks[0].document_key == "doc-001"
    assert chunks[0].chunk_index == 0


def test_preview_script_can_parse_case_001(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main([str(DATA_ROOT / "case-001-individual-buyer-mortgage")])

    captured = capsys.readouterr().out
    assert exit_code == 0
    assert "Matter title: Pukekohe Purchase for the Ngata Family" in captured
    assert "Document count: 5" in captured
    assert "Page count:" in captured
    assert "Chunk count:" in captured
