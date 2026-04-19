from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


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
