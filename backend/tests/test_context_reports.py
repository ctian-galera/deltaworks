import pytest
from sqlalchemy.exc import IntegrityError
from uuid import uuid4

from app.models.engineering_change import EngineeringChange
from app.schemas.engineering_context_report import EngineeringContextReportCreate
from app.services.engineering_context_report import (
    create_context_report,
    get_context_report_by_event_id,
    get_context_reports,
)


def create_test_engineering_change(db_session):
    change = EngineeringChange(
        change_number=f"ECR-TEST-{uuid4().hex[:8].upper()}",
        title="Test engineering change",
        description="Automated test engineering change.",
    )

    db_session.add(change)
    db_session.commit()
    db_session.refresh(change)

    return change


def create_test_report_data(event_id):
    return EngineeringContextReportCreate(
        event_id=event_id,
        model="test-model",
        prompt_version="v1",
        input_context={
            "ecr": {
                "id": 1,
                "title": "Test ECR",
                "status": "DRAFT",
            }
        },
        report={
            "reviewer_attention": "Test report.",
            "critical_risks": [],
            "warning_risks": [],
            "required_approvals": [],
        },
    )


def test_create_context_report(db_session):
    change = create_test_engineering_change(db_session)
    event_id = uuid4()

    data = create_test_report_data(event_id)

    report = create_context_report(
        db_session,
        change.id,
        data,
    )

    assert report.id is not None
    assert report.event_id == event_id
    assert report.engineering_change_id == change.id
    assert report.model == "test-model"
    assert report.prompt_version == "v1"
    assert report.report["reviewer_attention"] == "Test report."


def test_get_context_report_by_event_id(db_session):
    change = create_test_engineering_change(db_session)
    event_id = uuid4()

    data = create_test_report_data(event_id)

    created = create_context_report(
        db_session,
        change.id,
        data,
    )

    result = get_context_report_by_event_id(
        db_session,
        event_id,
    )

    assert result is not None
    assert result.id == created.id
    assert result.event_id == event_id
    assert result.engineering_change_id == change.id


def test_get_context_report_by_event_id_not_found(db_session):
    result = get_context_report_by_event_id(
        db_session,
        uuid4(),
    )

    assert result is None


def test_get_context_reports(db_session):
    change = create_test_engineering_change(db_session)

    first_event_id = uuid4()
    second_event_id = uuid4()

    create_context_report(
        db_session,
        change.id,
        create_test_report_data(first_event_id),
    )

    create_context_report(
        db_session,
        change.id,
        create_test_report_data(second_event_id),
    )

    reports = get_context_reports(
        db_session,
        change.id,
    )

    assert len(reports) == 2
    assert {
        report.event_id
        for report in reports
    } == {
        first_event_id,
        second_event_id,
    }


def test_duplicate_event_id_is_rejected(db_session):
    change = create_test_engineering_change(db_session)
    event_id = uuid4()

    data = create_test_report_data(event_id)

    create_context_report(
        db_session,
        change.id,
        data,
    )

    with pytest.raises(IntegrityError):
        create_context_report(
            db_session,
            change.id,
            data,
        )