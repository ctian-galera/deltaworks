from uuid import UUID

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
    ApprovalRequiredError,
    create_engineering_change,
    transition_engineering_change,
)
from app.workflows.engineering_change import (
    InvalidChangeTransition,
)
from app.schemas.change_action import (
    ChangeActionCreate,
    ChangeActionResponse,
)

from app.services.change_action import (
    ChangeActionScopeLockedError,
    create_change_action,
    get_change_actions,
)
from app.risk.service import (
    evaluate_and_persist_change,
    get_change_risks,
)
from app.schemas.risk import RiskFindingResponse
from app.policy.service import (
    generate_approval_requirements,
    get_change_approvals,
    decide_approval,
)
from app.schemas.approval_requirement import (
    ApprovalRequirementResponse,
    ApprovalRequirementDecision,
)
from app.schemas.engineering_change_bundle import EngineeringChangeBundleResponse
from app.schemas.engineering_context_report import (
    EngineeringContextReportCreate,
    EngineeringContextReportResponse,
)
from app.services.engineering_context_report import (
    create_context_report,
    get_context_reports,
    get_context_report_by_event_id,
    get_report_by_event,
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


@router.get(
    "/{change_id}",
    response_model=EngineeringChangeRead,
)
def get_change(
    change_id: int,
    db: Session = Depends(get_db),
):
    return get_change_or_404(
        change_id,
        db,
    )
    

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

    except ApprovalRequiredError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc

    except InvalidChangeTransition as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc
        

@router.post(
    "/{engineering_change_id}/evaluate",
    response_model=list[RiskFindingResponse],
)
def evaluate_engineering_change(
    engineering_change_id: int,
    db: Session = Depends(get_db),
):
    return evaluate_and_persist_change(
        db,
        engineering_change_id,
    )


@router.post(
    "/{engineering_change_id}/actions",
    response_model=ChangeActionResponse,
    status_code=201,
)
def create_engineering_change_action(
    engineering_change_id: int,
    data: ChangeActionCreate,
    db: Session = Depends(get_db),
):
    get_change_or_404(
        engineering_change_id,
        db,
    )

    try:
        return create_change_action(
            db,
            engineering_change_id,
            data,
        )
    except ChangeActionScopeLockedError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc



@router.get(
    "/{engineering_change_id}/actions",
    response_model=list[ChangeActionResponse],
)
def get_engineering_change_actions(
    engineering_change_id: int,
    db: Session = Depends(get_db),
):
    get_change_or_404(engineering_change_id, db)

    return get_change_actions(
        db,
        engineering_change_id,
    )
    
    



@router.get(
    "/{engineering_change_id}/risks",
    response_model=list[RiskFindingResponse],
)
def get_engineering_change_risks(
    engineering_change_id: int,
    db: Session = Depends(get_db),
):
    return get_change_risks(
        db,
        engineering_change_id,
    )
    
    
@router.post(
    "/{engineering_change_id}/approvals/generate",
    response_model=list[ApprovalRequirementResponse],
)
def generate_engineering_change_approvals(
    engineering_change_id: int,
    db: Session = Depends(get_db),
):
    get_change_or_404(engineering_change_id, db)

    return generate_approval_requirements(
        db,
        engineering_change_id,
    )


@router.get(
    "/{engineering_change_id}/approvals",
    response_model=list[ApprovalRequirementResponse],
)
def get_engineering_change_approvals(
    engineering_change_id: int,
    db: Session = Depends(get_db),
):
    get_change_or_404(engineering_change_id, db)

    return get_change_approvals(
        db,
        engineering_change_id,
    )
    

@router.post(
    "/{engineering_change_id}/approvals/{approval_id}/decision",
    response_model=ApprovalRequirementResponse,
)
def decide_engineering_change_approval(
    engineering_change_id: int,
    approval_id: UUID,
    data: ApprovalRequirementDecision,
    db: Session = Depends(get_db),
):
    get_change_or_404(engineering_change_id, db)

    try:
        return decide_approval(
            db,
            engineering_change_id,
            approval_id,
            data.status,
            data.actor,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=409,
            detail=str(exc),
        ) from exc
        
        
@router.get(
    "/{engineering_change_id}/context-bundle",
    response_model=EngineeringChangeBundleResponse,
)
def get_engineering_change_context_bundle(
    engineering_change_id: int,
    db: Session = Depends(get_db),
):
    change = get_change_or_404(
        engineering_change_id,
        db,
    )

    return {
        "ecr": change,
        "risks": get_change_risks(db, engineering_change_id),
        "approvals": get_change_approvals(db, engineering_change_id),
    }
    
@router.post(
    "/{engineering_change_id}/context-reports",
    response_model=EngineeringContextReportResponse,
    status_code=201,
)
def create_engineering_context_report(
    engineering_change_id: int,
    data: EngineeringContextReportCreate,
    db: Session = Depends(get_db),
):
    get_change_or_404(
        engineering_change_id,
        db,
    )

    existing_report = get_context_report_by_event_id(
        db,
        data.event_id,
    )

    if existing_report is not None:
        return existing_report

    return create_context_report(
        db,
        engineering_change_id,
        data,
    )
    
    
@router.get(
    "/{engineering_change_id}/context-reports",
    response_model=list[EngineeringContextReportResponse],
)
def get_engineering_context_reports(
    engineering_change_id: int,
    db: Session = Depends(get_db),
):
    get_change_or_404(
        engineering_change_id,
        db,
    )

    return get_context_reports(
        db,
        engineering_change_id,
    )


@router.get(
    "/{engineering_change_id}/context-reports/events/{event_id}",
    response_model=EngineeringContextReportResponse,
)
def get_engineering_context_report_by_event(
    engineering_change_id: int,
    event_id: UUID,
    db: Session = Depends(get_db),
):
    get_change_or_404(
        engineering_change_id,
        db,
    )

    report = get_report_by_event(
        db,
        engineering_change_id,
        event_id,
    )

    if report is None:
        raise HTTPException(
            status_code=404,
            detail="Context report not found for this event",
        )

    return report