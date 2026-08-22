from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.services.engineering_context_report import create_context_report
from app.schemas.engineering_context_report import EngineeringContextReportCreate
from app.models.engineering_change import EngineeringChange


def create_test_engineering_change(db_session):
    change = EngineeringChange(
        change_number=f"ECR-API-{uuid4().hex[:8].upper()}",
        title="API test engineering change",
        description="Engineering change for API testing.",
    )

    db_session.add(change)
    db_session.commit()
    db_session.refresh(change)

    return change


def create_test_report(db_session, change_id, event_id):
    data = EngineeringContextReportCreate(
        event_id=event_id,
        model="test-model",
        prompt_version="v1",
        input_context={
            "ecr": {
                "id": change_id,
                "title": "API test ECR",
                "status": "DRAFT",
            }
        },
        report={
            "engineering_change_summary": {
                "change_number": "ECR-API-TEST",
                "title": "API test ECR",
                "status": "DRAFT",
                "description": "API test.",
            },
            "critical_risks": [],
            "warning_risks": [],
            "required_approvals": [],
            "reviewer_attention": "API test.",
        },
    )

    return create_context_report(
        db_session,
        change_id,
        data,
    )


def test_get_context_report_by_event_id(db_session, client):
    change = create_test_engineering_change(db_session)
    event_id = uuid4()

    report = create_test_report(
        db_session,
        change.id,
        event_id,
    )

    response = client.get(
        f"/api/v1/engineering-changes/{change.id}/context-reports/events/{event_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == str(report.id)
    assert data["event_id"] == str(event_id)
    assert data["engineering_change_id"] == change.id


def test_get_context_report_by_event_id_not_found(db_session, client):
    change = create_test_engineering_change(db_session)
    event_id = uuid4()

    response = client.get(
        f"/api/v1/engineering-changes/{change.id}/context-reports/events/{event_id}"
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Context report not found for this event"


def test_get_context_report_unknown_engineering_change(db_session, client):
    event_id = uuid4()

    response = client.get(
        f"/api/v1/engineering-changes/999999/context-reports/events/{event_id}"
    )

    assert response.status_code == 404