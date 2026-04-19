from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT_PATH = Path(__file__).resolve().parents[1] / "scripts" / "load_synthetic_matter.py"
SCRIPT_SPEC = importlib.util.spec_from_file_location("load_synthetic_matter", SCRIPT_PATH)
assert SCRIPT_SPEC is not None and SCRIPT_SPEC.loader is not None
SCRIPT_MODULE = importlib.util.module_from_spec(SCRIPT_SPEC)
SCRIPT_SPEC.loader.exec_module(SCRIPT_MODULE)
SYNTHETIC_DISCLAIMER = SCRIPT_MODULE.SYNTHETIC_DISCLAIMER
load_synthetic_matter = SCRIPT_MODULE.load_synthetic_matter

REPO_ROOT = Path(__file__).resolve().parents[3]
DATA_ROOT = REPO_ROOT / "synthetic-data" / "property-settlement"
CASE_IDS = [
    "case-001-individual-buyer-mortgage",
    "case-002-individual-vendor-discharge",
    "case-003-trust-buyer-mortgage-cdd",
    "case-004-trust-vendor-deed-variation",
]
REQUIRED_FILES = {
    "README.md",
    "matter.json",
    "documents.json",
    "ground_truth.json",
    "expected_questions.json",
}


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_synthetic_case_directory_exists(case_id: str) -> None:
    case_dir = DATA_ROOT / case_id
    assert case_dir.is_dir(), f"missing case directory: {case_dir}"


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_synthetic_case_has_required_files(case_id: str) -> None:
    case_dir = DATA_ROOT / case_id
    present_files = {item.name for item in case_dir.iterdir() if item.is_file()}
    assert REQUIRED_FILES.issubset(present_files)


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_every_synthetic_file_contains_disclaimer(case_id: str) -> None:
    case_dir = DATA_ROOT / case_id
    for filename in REQUIRED_FILES:
        content = (case_dir / filename).read_text(encoding="utf-8")
        assert SYNTHETIC_DISCLAIMER in content, f"{filename} missing disclaimer"


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_ground_truth_contains_expected_missing_items(case_id: str) -> None:
    case_dir = DATA_ROOT / case_id
    ground_truth = json.loads((case_dir / "ground_truth.json").read_text(encoding="utf-8"))
    assert "expected_missing_items" in ground_truth
    assert isinstance(ground_truth["expected_missing_items"], list)
    assert ground_truth["expected_missing_items"], "expected_missing_items should not be empty"


@pytest.mark.parametrize("case_id", CASE_IDS)
def test_expected_questions_has_at_least_three_questions(case_id: str) -> None:
    case_dir = DATA_ROOT / case_id
    expected_questions = json.loads(
        (case_dir / "expected_questions.json").read_text(encoding="utf-8")
    )
    assert len(expected_questions["questions"]) >= 3


def test_loader_can_parse_a_case_directory() -> None:
    case_dir = DATA_ROOT / "case-001-individual-buyer-mortgage"

    summary = load_synthetic_matter(case_dir)

    assert summary["matter_title"] == "Pukekohe Purchase for the Ngata Family"
    assert summary["matter_type"] == "individual_buyer_mortgage"
    assert summary["document_count"] == 5
    assert "proof of address" in " ".join(summary["expected_missing_items"]).lower()
