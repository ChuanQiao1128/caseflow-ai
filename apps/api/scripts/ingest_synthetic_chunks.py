from __future__ import annotations

import argparse
from pathlib import Path
from uuid import UUID

from caseflow_api.database import SessionLocal
from caseflow_api.ingestion.synthetic_ingestion import ingest_synthetic_case_chunks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest synthetic chunks into pgvector")
    parser.add_argument("organisation_id", type=UUID)
    parser.add_argument("matter_id", type=UUID)
    parser.add_argument("case_dir", type=Path)
    args = parser.parse_args(argv)

    with SessionLocal() as db:
        chunks = ingest_synthetic_case_chunks(
            db,
            organisation_id=args.organisation_id,
            matter_id=args.matter_id,
            case_dir=args.case_dir,
        )

    print(f"Ingested {len(chunks)} chunks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
