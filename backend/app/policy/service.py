from datetime import datetime, timezone

from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.approval_requirement import ApprovalRequirement, ApprovalStatus
from app.models.risk_finding import RiskFinding
from app.policy.engine import map_risk_to_approval


def generate_approval_requirements(
    db: Session,
    engineering_change_id: int,
) -> list[ApprovalRequirement]:

    db.execute(
        delete(ApprovalRequirement).where(
            ApprovalRequirement.engineering_change_id
            == engineering_change_id
        )
    )

    findings = list(
        db.scalars(
            select(RiskFinding).where(
                RiskFinding.engineering_change_id
                == engineering_change_id
            )
        ).all()
    )

    requirements: list[ApprovalRequirement] = []
    seen_roles = set()

    for finding in findings:
        role = map_risk_to_approval(
            finding.category,
            finding.severity,
        )

        if role is None or role in seen_roles:
            continue

        seen_roles.add(role)

        requirement = ApprovalRequirement(
            engineering_change_id=engineering_change_id,
            role=role,
            status=ApprovalStatus.PENDING,
        )

        db.add(requirement)
        requirements.append(requirement)

    db.commit()

    for requirement in requirements:
        db.refresh(requirement)

    return requirements


def get_change_approvals(
    db: Session,
    engineering_change_id: int,
) -> list[ApprovalRequirement]:

    return list(
        db.scalars(
            select(ApprovalRequirement)
            .where(
                ApprovalRequirement.engineering_change_id
                == engineering_change_id
            )
            .order_by(ApprovalRequirement.created_at)
        ).all()
    )
    

def decide_approval(
    db: Session,
    engineering_change_id: int,
    approval_id,
    status: ApprovalStatus,
    actor: str,
) -> ApprovalRequirement:
    approval = db.get(ApprovalRequirement, approval_id)

    if approval is None:
        raise ValueError("Approval requirement not found.")

    if approval.engineering_change_id != engineering_change_id:
        raise ValueError(
            "Approval requirement does not belong to this engineering change."
        )

    if approval.status != ApprovalStatus.PENDING:
        raise ValueError(
            "Approval requirement has already been decided."
        )

    approval.status = status
    approval.actor = actor
    approval.acted_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(approval)

    return approval