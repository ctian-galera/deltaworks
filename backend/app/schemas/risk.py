from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from app.models.risk_finding import RiskCategory, RiskSeverity


class RiskFindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    engineering_change_id: int
    node_id: UUID
    category: RiskCategory
    severity: RiskSeverity
    reason: str
    created_at: datetime