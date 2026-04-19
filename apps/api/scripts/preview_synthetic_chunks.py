from __future__ import annotations

import argparse
from pathlib import Path

from caseflow_api.ingestion.chunking import load_synthetic_case_summary


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Preview parsed synthetic source text chunks for a case directory"
    )
    parser.add_argument("case_dir", type=Path)
    args = parser.parse_args(argv)

    summary = load_synthetic_case_summary(args.case_dir)
    print(f"Matter title: {summary['matter_title']}")
    print(f"Document count: {summary['document_count']}")
    print(f"Page count: {summary['page_count']}")
    print(f"Chunk count: {summary['chunk_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
