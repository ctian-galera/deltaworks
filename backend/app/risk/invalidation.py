from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.models.approval_requirement import ApprovalRequirement
from app.models.risk_finding import RiskFinding


def invalidate_change_evaluation(
    db: Session,
    engineering_change_id: int,
) -> None:
    db.execute(
        delete(RiskFinding).where(
            RiskFinding.engineering_change_id == engineering_change_id
        )
    )

    db.execute(
        delete(ApprovalRequirement).where(
            ApprovalRequirement.engineering_change_id == engineering_change_id
        )
    )