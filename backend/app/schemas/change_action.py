from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.change_action import ChangeActionType


class ChangeActionCreate(BaseModel):
    node_id: UUID
    action: ChangeActionType
    proposed_state: dict = Field(default_factory=dict)


class ChangeActionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    engineering_change_id: int
    node_id: UUID
    action: ChangeActionType
    proposed_state: dict
    created_at: datetime