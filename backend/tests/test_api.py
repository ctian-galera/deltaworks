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
    
    

def test_create_engineering_change(client):
    response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "API test engineering change",
            "description": "Testing ECR creation through the API.",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] is not None
    assert data["change_number"].startswith("ECR-")
    assert data["title"] == "API test engineering change"
    assert data["description"] == "Testing ECR creation through the API."
    assert data["status"] == "DRAFT"


def test_get_engineering_change(client):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Get API test",
            "description": "Testing ECR retrieval.",
        },
    )

    assert create_response.status_code == 201

    created = create_response.json()
    change_id = created["id"]

    response = client.get(
        f"/api/v1/engineering-changes/{change_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == change_id
    assert data["change_number"] == created["change_number"]
    assert data["title"] == "Get API test"
    assert data["description"] == "Testing ECR retrieval."
    assert data["status"] == "DRAFT"


def test_get_engineering_change_not_found(client):
    response = client.get(
        "/api/v1/engineering-changes/999999"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Engineering change not found"


def test_submit_engineering_change(client):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "change_number": "ECR-API-TEST-003",
            "title": "Submit API test",
            "description": "Testing ECR submission.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/engineering-changes/{change_id}/submit"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == change_id
    assert data["status"] == "SUBMITTED"


def test_submit_engineering_change_invalid_transition(client):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "change_number": "ECR-API-TEST-004",
            "title": "Invalid transition test",
            "description": "Testing invalid ECR submission.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    # First submission is valid.
    first_response = client.post(
        f"/api/v1/engineering-changes/{change_id}/submit"
    )

    assert first_response.status_code == 200
    assert first_response.json()["status"] == "SUBMITTED"

    # Submitting an already-submitted ECR should fail.
    second_response = client.post(
        f"/api/v1/engineering-changes/{change_id}/submit"
    )

    assert second_response.status_code == 409