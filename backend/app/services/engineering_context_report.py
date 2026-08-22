from uuid import UUID

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
        event_id=data.event_id,
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


def get_context_report_by_event_id(
    db: Session,
    event_id: UUID,
) -> EngineeringContextReport | None:

    stmt = (
        select(EngineeringContextReport)
        .where(
            EngineeringContextReport.event_id == event_id
        )
    )

    return db.scalar(stmt)


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


def get_report_by_event(
    db: Session,
    engineering_change_id: int,
    event_id: UUID,
) -> EngineeringContextReport | None:

    stmt = (
        select(EngineeringContextReport)
        .where(
            EngineeringContextReport.engineering_change_id
            == engineering_change_id,
            EngineeringContextReport.event_id == event_id,
        )
    )

    return db.scalars(stmt).first()