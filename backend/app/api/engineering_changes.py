from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.engineering_change import (
    ChangeStatus,
    EngineeringChange,
)
from app.schemas.engineering_change import (
    EngineeringChangeCreate,
    EngineeringChangeRead,
    EngineeringChangeTransition
)
from app.services.engineering_change import (
    create_engineering_change,
    transition_engineering_change,
)
from app.workflows.engineering_change import (
    InvalidChangeTransition,
)

router = APIRouter(
    prefix="/engineering-changes",
    tags=["Engineering Changes"],
)


@router.post(
    "",
    response_model=EngineeringChangeRead,
    status_code=201,
)
def create_change(
    data: EngineeringChangeCreate,
    db: Session = Depends(get_db),
):
    return create_engineering_change(db, data)


# helper
def get_change_or_404(
    change_id: int,
    db: Session,
) -> EngineeringChange:
    change = db.get(EngineeringChange, change_id)

    if change is None:
        raise HTTPException(
            status_code=404,
            detail="Engineering change not found",
        )

    return change


@router.post(
    "/{change_id}/submit",
    response_model=EngineeringChangeRead,
)
def submit_change(
    change_id: int,
    db: Session = Depends(get_db),
):
    change = get_change_or_404(change_id, db)

    try:
        return transition_engineering_change(
            db,
            change,
            ChangeStatus.SUBMITTED,
        )
    except InvalidChangeTransition as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc
        

@router.post(
    "/{change_id}/transition",
    response_model=EngineeringChangeRead,
)
def transition_change(
    change_id: int,
    data: EngineeringChangeTransition,
    db: Session = Depends(get_db),
):
    change = get_change_or_404(change_id, db)

    try:
        return transition_engineering_change(
            db,
            change,
            data.target_status,
            actor=data.actor,
            reason=data.reason,
        )
    except InvalidChangeTransition as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc