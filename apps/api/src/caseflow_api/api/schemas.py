from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class OrganisationCreate(BaseModel):
    name: str


class OrganisationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    created_at: datetime
    updated_at: datetime | None = None


class MatterCreate(BaseModel):
    reference: str | None = None
    title: str


class MatterRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organisation_id: UUID
    reference: str | None = None
    title: str
    status: str
    created_at: datetime
    updated_at: datetime | None = None


class DocumentCreate(BaseModel):
    filename: str
    mime_type: str
    storage_key: str


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    matter_id: UUID
    filename: str
    mime_type: str
    storage_key: str
    created_at: datetime
    updated_at: datetime | None = None


class AuditLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organisation_id: UUID
    actor_user_id: UUID | None = None
    action: str
    entity_type: str
    entity_id: str
    details: dict[str, object]
    created_at: datetime
    updated_at: datetime | None = None


class EvidenceChunkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    chunk_id: UUID
    document_id: UUID
    page_number: int | None = None
    chunk_index: int
    content: str
    score: float
    citation: str


class MatterSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=20)


class MatterSearchResponse(BaseModel):
    organisation_id: UUID
    matter_id: UUID
    query: str
    results: list[EvidenceChunkRead]
    confidence: str
    has_evidence: bool
    message: str | None = None


class ExtractedFieldRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    field_name: str
    value: str | None = None
    confidence: float = Field(ge=0.0, le=1.0)
    citation: str


class MatterExtractionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    matter_id: UUID
    extracted_fields: list[ExtractedFieldRead] = Field(default_factory=list)


class ChecklistFindingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    item_name: str
    status: Literal["pass", "fail", "unclear"]
    citation: str | None = None
    reason: str | None = None

    @model_validator(mode="after")
    def validate_unclear_reason_and_citation(self) -> ChecklistFindingRead:
        if self.status == "unclear" and not self.reason:
            raise ValueError("unclear findings require a reason")
        if self.status == "unclear" and not self.citation:
            raise ValueError("unclear findings require a citation")
        return self


class ChecklistResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    matter_id: UUID
    findings: list[ChecklistFindingRead] = Field(default_factory=list)


class ReviewBoundednessRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    is_bounded: bool = True
    is_legal_advice: bool = False
    disclaimer: str = (
        "This review is a bounded human review aid, not legal advice or a legal approval. "
        "It highlights extracted evidence and checklist findings for manual review."
    )


class ReviewDecisionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    review_summary: str
    overall_status: Literal[
        "needs_human_review",
        "ready_for_review",
        "insufficient_evidence",
    ]
    extracted_fields: list[ExtractedFieldRead] = Field(default_factory=list)
    checklist_findings: list[ChecklistFindingRead] = Field(default_factory=list)
    boundedness: ReviewBoundednessRead = Field(default_factory=ReviewBoundednessRead)
