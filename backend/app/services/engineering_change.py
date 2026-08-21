from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.approval_requirement import (
    ApprovalRequirement,
    ApprovalStatus,
)
from app.models.engineering_change import (
    ChangeStatus,
    EngineeringChange,
)
from app.schemas.engineering_change import EngineeringChangeCreate
from app.workflows.engineering_change import transition
from app.services.audit import record_audit_event
from app.events.engineering_change import build_status_changed_event
from app.events.publisher import publish_event


class ApprovalRequiredError(Exception):
    pass


def create_engineering_change(
    db: Session,
    data: EngineeringChangeCreate,
) -> EngineeringChange:
    change = EngineeringChange(
        change_number="TEMP",
        title=data.title,
        description=data.description,
    )

    db.add(change)
    db.flush()

    change.change_number = f"ECR-{change.created_at.year}-{change.id:05d}"

    db.commit()
    db.refresh(change)

    return change


def transition_engineering_change(
    db: Session,
    change: EngineeringChange,
    target_status: ChangeStatus,
    *,
    actor: str = "system",
    reason: str | None = None,
) -> EngineeringChange:

    if (
        change.status == ChangeStatus.UNDER_REVIEW
        and target_status == ChangeStatus.APPROVED
    ):
        pending_approvals = db.scalars(
            select(ApprovalRequirement).where(
                ApprovalRequirement.engineering_change_id == change.id,
                ApprovalRequirement.status == ApprovalStatus.PENDING,
            )
        ).all()

        if pending_approvals:
            raise ApprovalRequiredError(
                "Engineering change cannot be approved while "
                "required approvals are still pending."
            )

    previous_status = change.status

    change.status = transition(
        change.status,
        target_status,
    )

    record_audit_event(
        db,
        engineering_change_id=change.id,
        event_type="STATUS_CHANGED",
        actor=actor,
        from_status=previous_status.value,
        to_status=target_status.value,
        reason=reason,
    )

    db.commit()
    db.refresh(change)

    publish_event(
        build_status_changed_event(
            change_id=change.id,
            change_number=change.change_number,
            previous_status=previous_status,
            new_status=target_status,
        )
    )

    return change