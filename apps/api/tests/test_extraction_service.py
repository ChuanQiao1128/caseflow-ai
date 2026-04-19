from __future__ import annotations

from types import SimpleNamespace
from uuid import UUID

from caseflow_api.retrieval.evidence import EvidenceCitation
from caseflow_api.retrieval.service import MatterRetrievalResult


def test_extract_matter_fields_uses_retrieval_and_returns_citations(monkeypatch) -> None:
    calls: list[tuple[str, UUID, UUID, str]] = []

    def fake_search_matter_evidence(*, db, organisation_id, matter_id, query, limit=5, max_distance=0.95):
        calls.append((db, organisation_id, matter_id, query))
        return MatterRetrievalResult(
            organisation_id=organisation_id,
            matter_id=matter_id,
            query=query,
            confidence="high",
            has_evidence=True,
            results=[
                EvidenceCitation(
                    chunk_id=UUID("11111111-1111-1111-1111-111111111111"),
                    document_id=UUID("22222222-2222-2222-2222-222222222222"),
                    page_number=3,
                    chunk_index=1,
                    content="Settlement date: 30 April 2026.",
                    score=0.12,
                    citation="document 22222222-2222-2222-2222-222222222222 (page 3, chunk 1)",
                )
            ],
        )

    monkeypatch.setattr("caseflow_api.extraction.service.search_matter_evidence", fake_search_matter_evidence)

    from caseflow_api.extraction.service import ExtractionFieldSpec, extract_matter_fields

    db = SimpleNamespace(name="db")
    response = extract_matter_fields(
        db=db,
        organisation_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        matter_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        field_specs=[ExtractionFieldSpec(field_name="settlement_date", query="settlement date")],
    )

    assert len(calls) == 1
    assert calls[0][3] == "settlement date"
    assert response.matter_id == UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
    assert response.extracted_fields[0].field_name == "settlement_date"
    assert response.extracted_fields[0].value == "30 April 2026"
    assert response.extracted_fields[0].confidence == 0.9
    assert response.extracted_fields[0].citation == "document 22222222-2222-2222-2222-222222222222 (page 3, chunk 1)"


def test_extract_matter_fields_returns_unclear_when_evidence_is_missing(monkeypatch) -> None:
    def fake_search_matter_evidence(*, db, organisation_id, matter_id, query, limit=5, max_distance=0.95):
        return MatterRetrievalResult(
            organisation_id=organisation_id,
            matter_id=matter_id,
            query=query,
            confidence="low",
            has_evidence=False,
            results=[],
            message="No relevant evidence found",
        )

    monkeypatch.setattr("caseflow_api.extraction.service.search_matter_evidence", fake_search_matter_evidence)

    from caseflow_api.extraction.service import ExtractionFieldSpec, extract_matter_fields

    response = extract_matter_fields(
        db=SimpleNamespace(name="db"),
        organisation_id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        matter_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        field_specs=[ExtractionFieldSpec(field_name="deposit_amount", query="deposit amount")],
    )

    extracted = response.extracted_fields[0]
    assert extracted.field_name == "deposit_amount"
    assert extracted.value is None
    assert extracted.confidence == 0.0
    assert extracted.citation == "needs_human_review"
