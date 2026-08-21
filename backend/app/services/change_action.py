from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.change_action import ChangeAction
from app.schemas.change_action import ChangeActionCreate


def create_change_action(
    db: Session,
    engineering_change_id: int,
    data: ChangeActionCreate,
) -> ChangeAction:
    action = ChangeAction(
        engineering_change_id=engineering_change_id,
        node_id=data.node_id,
        action=data.action,
        proposed_state=data.proposed_state,
    )

    db.add(action)
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