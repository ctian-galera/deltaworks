from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.engineering_context_report import EngineeringContextReport
from app.schemas.engineering_context_report import (
    EngineeringContextReportCreate,
)


def create_context_report(
    db: Session,
    engineering_change_id: int,
    data: EngineeringContextReportCreate,
) -> EngineeringContextReport:

    report = EngineeringContextReport(
        engineering_change_id=engineering_change_id,
        model=data.model,
        prompt_version=data.prompt_version,
        input_context=data.input_context,
        report=data.report,
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report


def get_context_reports(
    db: Session,
    engineering_change_id: int,
) -> list[EngineeringContextReport]:

    stmt = (
        select(EngineeringContextReport)
        .where(
            EngineeringContextReport.engineering_change_id
            == engineering_change_id
        )
        .order_by(
            EngineeringContextReport.created_at.desc()
        )
    )

    return list(db.scalars(stmt).all())