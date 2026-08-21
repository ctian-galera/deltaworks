from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.context_edge import ContextRelationshipType
from app.models.context_node import ContextNodeType


class ContextNodeCreate(BaseModel):
    site_id: str = Field(min_length=1, max_length=50)
    type: ContextNodeType
    identifier: str = Field(min_length=1, max_length=100)
    name: str = Field(min_length=1, max_length=200)
    metadata: dict = Field(default_factory=dict)


class ContextNodeResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: UUID
    site_id: str
    type: ContextNodeType
    identifier: str
    name: str
    metadata: dict = Field(
        validation_alias="metadata_json",
        serialization_alias="metadata",
    )
    created_at: datetime
    updated_at: datetime


class ContextEdgeCreate(BaseModel):
    parent_id: UUID
    child_id: UUID
    relationship_type: ContextRelationshipType
    metadata: dict = Field(default_factory=dict)


class ContextEdgeResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
    )

    id: UUID
    parent_id: UUID
    child_id: UUID
    relationship_type: ContextRelationshipType
    metadata: dict = Field(
        validation_alias="metadata_json",
        serialization_alias="metadata",
    )
    created_at: datetime