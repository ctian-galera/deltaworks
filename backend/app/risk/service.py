from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.models.risk_finding import RiskFinding as RiskFindingModel
from app.risk.engine import evaluate_change
from app.risk.types import RiskFinding


def evaluate_and_persist_change(
    db: Session,
    engineering_change_id: int,
    max_depth: int = 3,
) -> list[RiskFindingModel]:
    """
    Evaluate an engineering change and replace its existing findings.

    Evaluation is intentionally idempotent:
    running it twice produces the current set of findings,
    rather than accumulating duplicates.
    """

    db.execute(
        delete(RiskFindingModel).where(
            RiskFindingModel.engineering_change_id
            == engineering_change_id
        )
    )

    findings = evaluate_change(
        db,
        engineering_change_id,
        max_depth=max_depth,
    )

    persisted: list[RiskFindingModel] = []

    for finding in findings:
        model = RiskFindingModel(
            engineering_change_id=engineering_change_id,
            node_id=finding.node_id,
            category=finding.category.value,
            severity=finding.severity.value,
            reason=finding.reason,
        )

        db.add(model)
        persisted.append(model)

    db.commit()

    for model in persisted:
        db.refresh(model)

    return persisted


def get_change_risks(
    db: Session,
    engineering_change_id: int,
) -> list[RiskFindingModel]:
    return list(
        db.scalars(
            select(RiskFindingModel)
            .where(
                RiskFindingModel.engineering_change_id
                == engineering_change_id
            )
            .order_by(
                RiskFindingModel.created_at,
            )
        ).all()
    )