from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.approval_requirement import (
    ApprovalRole,
    ApprovalStatus,
)


class ApprovalRequirementResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    engineering_change_id: int
    role: ApprovalRole
    status: ApprovalStatus
    actor: str | None
    acted_at: datetime | None
    created_at: datetime
    
    
class ApprovalRequirementDecision(BaseModel):
    status: ApprovalStatus
    actor: str