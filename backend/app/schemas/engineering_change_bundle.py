from pydantic import BaseModel

from app.schemas.engineering_change import EngineeringChangeRead
from app.schemas.risk import RiskFindingResponse
from app.schemas.approval_requirement import ApprovalRequirementResponse


class EngineeringChangeBundleResponse(BaseModel):
    ecr: EngineeringChangeRead
    risks: list[RiskFindingResponse]
    approvals: list[ApprovalRequirementResponse]