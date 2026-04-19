from __future__ import annotations

import argparse
from uuid import UUID

from caseflow_api.ai.embeddings import embed_query
from caseflow_api.database import SessionLocal
from caseflow_api.retrieval.vector_search import search_document_chunks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Search synthetic chunks with embeddings")
    parser.add_argument("organisation_id", type=UUID)
    parser.add_argument("matter_id", type=UUID)
    parser.add_argument("query_text", type=str)
    parser.add_argument("--limit", type=int, default=5)
    args = parser.parse_args(argv)

    query_embedding = embed_query(args.query_text)
    with SessionLocal() as db:
        results = search_document_chunks(
            db=db,
            organisation_id=args.organisation_id,
            matter_id=args.matter_id,
            query_embedding=query_embedding,
            limit=args.limit,
        )

    for result in results:
        preview = result.content[:160].replace("\n", " ")
        print(
            f"document_id={result.document_id} "
            f"page_number={result.page_number} score={result.score:.6f}"
        )
        print(f"preview={preview}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
