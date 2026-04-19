from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

SYNTHETIC_DISCLAIMER = "SYNTHETIC DEMO DATA — NOT REAL CLIENT DATA"
REQUIRED_FILES = (
    "README.md",
    "matter.json",
    "documents.json",
    "ground_truth.json",
    "expected_questions.json",
)


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(_read_text(path))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return payload


def load_synthetic_matter(case_dir: Path) -> dict[str, Any]:
    case_dir = case_dir.expanduser().resolve()
    if not case_dir.is_dir():
        raise FileNotFoundError(f"Synthetic case directory not found: {case_dir}")

    missing = [name for name in REQUIRED_FILES if not (case_dir / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing required files: {', '.join(missing)}")

    for filename in REQUIRED_FILES:
        content = _read_text(case_dir / filename)
        if SYNTHETIC_DISCLAIMER not in content:
            raise ValueError(f"{filename} missing synthetic disclaimer")

    matter = _load_json(case_dir / "matter.json")
    documents = _load_json(case_dir / "documents.json")
    ground_truth = _load_json(case_dir / "ground_truth.json")
    expected_questions = _load_json(case_dir / "expected_questions.json")

    expected_missing_items = ground_truth.get("expected_missing_items")
    if not isinstance(expected_missing_items, list):
        raise ValueError("ground_truth.json must contain expected_missing_items as a list")

    questions = expected_questions.get("questions")
    if not isinstance(questions, list):
        raise ValueError("expected_questions.json must contain questions as a list")

    document_entries = documents.get("documents")
    if not isinstance(document_entries, list):
        raise ValueError("documents.json must contain documents as a list")

    summary = {
        "matter_title": matter.get("matter_title"),
        "matter_type": matter.get("matter_type"),
        "document_count": len(document_entries),
        "expected_missing_items": expected_missing_items,
    }
    return summary


def build_summary_text(case_dir: Path, summary: dict[str, Any]) -> str:
    return (
        f"Matter: {summary['matter_title']}\n"
        f"Type: {summary['matter_type']}\n"
        f"Documents: {summary['document_count']}\n"
        f"Expected missing items: {', '.join(summary['expected_missing_items'])}\n"
        f"Case directory: {case_dir}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Load a synthetic property settlement matter")
    parser.add_argument("case_dir", type=Path)
    args = parser.parse_args()

    summary = load_synthetic_matter(args.case_dir)
    print(build_summary_text(args.case_dir.expanduser().resolve(), summary), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
