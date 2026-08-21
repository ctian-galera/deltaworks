from sqlalchemy.orm import Session

from app.models.engineering_change import ChangeStatus, EngineeringChange
from app.schemas.engineering_change import EngineeringChangeCreate
from app.workflows.engineering_change import transition
from app.services.audit import record_audit_event


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

    return change