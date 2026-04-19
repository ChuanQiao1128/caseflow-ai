from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from caseflow_api.api.schemas import ExtractedFieldRead, MatterExtractionResponse
from caseflow_api.retrieval.service import search_matter_evidence


@dataclass(frozen=True, slots=True)
class ExtractionFieldSpec:
    field_name: str
    query: str


def _extract_value_from_content(field_name: str, content: str) -> str | None:
    normalized = content.strip().rstrip(".")
    if ":" in normalized:
        left, right = normalized.split(":", 1)
        if field_name.replace("_", " ").lower() in left.lower():
            value = right.strip().rstrip(".")
            return value or None
    return None


def extract_matter_fields(
    *,
    db: Session,
    organisation_id: UUID,
    matter_id: UUID,
    field_specs: list[ExtractionFieldSpec],
) -> MatterExtractionResponse:
    extracted_fields: list[ExtractedFieldRead] = []

    for field_spec in field_specs:
        retrieval = search_matter_evidence(
            db=db,
            organisation_id=organisation_id,
            matter_id=matter_id,
            query=field_spec.query,
        )

        if not retrieval.has_evidence or not retrieval.results:
            extracted_fields.append(
                ExtractedFieldRead(
                    field_name=field_spec.field_name,
                    value=None,
                    confidence=0.0,
                    citation="needs_human_review",
                )
            )
            continue

        best_match = retrieval.results[0]
        value = _extract_value_from_content(field_spec.field_name, best_match.content)
        if value is None:
            extracted_fields.append(
                ExtractedFieldRead(
                    field_name=field_spec.field_name,
                    value=None,
                    confidence=0.0,
                    citation=best_match.citation,
                )
            )
            continue

        extracted_fields.append(
            ExtractedFieldRead(
                field_name=field_spec.field_name,
                value=value,
                confidence=0.9,
                citation=best_match.citation,
            )
        )

    return MatterExtractionResponse(matter_id=matter_id, extracted_fields=extracted_fields)
