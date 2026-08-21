from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.change_action import ChangeAction
from app.models.engineering_change import ChangeStatus, EngineeringChange
from app.schemas.change_action import ChangeActionCreate
from app.risk.invalidation import invalidate_change_evaluation


class ChangeActionError(Exception):
    """Base exception for change-action validation errors."""


class ChangeActionScopeLockedError(ChangeActionError):
    """Raised when an ECR is no longer editable."""


def create_change_action(
    db: Session,
    engineering_change_id: int,
    data: ChangeActionCreate,
) -> ChangeAction:
    change = db.get(
        EngineeringChange,
        engineering_change_id,
    )

    if change is None:
        raise ChangeActionError(
            "Engineering change not found."
        )

    if change.status != ChangeStatus.DRAFT:
        raise ChangeActionScopeLockedError(
            "Change actions can only be modified while the "
            "engineering change is in DRAFT."
        )

    action = ChangeAction(
        engineering_change_id=engineering_change_id,
        node_id=data.node_id,
        action=data.action,
        proposed_state=data.proposed_state,
    )

    db.add(action)

    invalidate_change_evaluation(
        db,
        engineering_change_id,
    )

    db.commit()
    db.refresh(action)

    return action


def get_change_actions(
    db: Session,
    engineering_change_id: int,
) -> list[ChangeAction]:
    statement = (
        select(ChangeAction)
        .where(
            ChangeAction.engineering_change_id
            == engineering_change_id
        )
        .order_by(ChangeAction.created_at)
    )

    return list(db.scalars(statement).all())
