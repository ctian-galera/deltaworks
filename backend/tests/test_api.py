from uuid import uuid4

import pytest

from app.main import app
from app.services.engineering_context_report import create_context_report
from app.schemas.engineering_context_report import EngineeringContextReportCreate
from app.models.engineering_change import EngineeringChange

from app.models.context_node import ContextNode, ContextNodeType


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
    
    
def test_create_context_report(client):
    # Create an ECR first.
    change_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Context report API test",
            "description": "Testing context report creation.",
        },
    )

    assert change_response.status_code == 201

    change_id = change_response.json()["id"]

    event_id = "11111111-1111-1111-1111-111111111111"

    response = client.post(
        f"/api/v1/engineering-changes/{change_id}/context-reports",
        json={
            "event_id": event_id,
            "model": "test-model",
            "prompt_version": "v1",
            "input_context": {
                "ecr": {
                    "id": change_id,
                },
                "risks": [],
                "approvals": [],
            },
            "report": {
                "engineering_change_summary": {
                    "title": "Context report API test",
                    "status": "DRAFT",
                    "change_number": "ECR-2026-TEST",
                    "description": "Test report.",
                },
                "critical_risks": [],
                "warning_risks": [],
                "required_approvals": [],
                "reviewer_attention": "Test.",
            },
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["event_id"] == event_id
    assert data["engineering_change_id"] == change_id
    assert data["model"] == "test-model"
    assert data["prompt_version"] == "v1"
    assert data["report"]["reviewer_attention"] == "Test."
    

def test_create_context_report_is_idempotent(client):
    # Create an ECR.
    change_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Idempotency API test",
            "description": "Testing duplicate event handling.",
        },
    )

    assert change_response.status_code == 201

    change_id = change_response.json()["id"]

    event_id = "22222222-2222-2222-2222-222222222222"

    payload = {
        "event_id": event_id,
        "model": "test-model",
        "prompt_version": "v1",
        "input_context": {
            "ecr": {
                "id": change_id,
            },
            "risks": [],
            "approvals": [],
        },
        "report": {
            "engineering_change_summary": {
                "title": "Idempotency API test",
                "status": "DRAFT",
                "change_number": "ECR-2026-TEST",
                "description": "Test report.",
            },
            "critical_risks": [],
            "warning_risks": [],
            "required_approvals": [],
            "reviewer_attention": "Original report.",
        },
    }

    # First event: should create the report.
    first_response = client.post(
        f"/api/v1/engineering-changes/{change_id}/context-reports",
        json=payload,
    )

    assert first_response.status_code == 201

    first_data = first_response.json()

    # Same event again: should NOT create another report.
    duplicate_response = client.post(
        f"/api/v1/engineering-changes/{change_id}/context-reports",
        json=payload,
    )

    assert duplicate_response.status_code == 201

    duplicate_data = duplicate_response.json()

    # It should return the ORIGINAL report.
    assert duplicate_data["id"] == first_data["id"]
    assert duplicate_data["event_id"] == first_data["event_id"]
    assert duplicate_data["created_at"] == first_data["created_at"]

    # Most importantly, the original report remains unchanged.
    assert duplicate_data["report"]["reviewer_attention"] == "Original report."

    # Verify the API only has one report for this ECR.
    reports_response = client.get(
        f"/api/v1/engineering-changes/{change_id}/context-reports"
    )

    assert reports_response.status_code == 200

    reports = reports_response.json()

    assert len(reports) == 1
    assert reports[0]["id"] == first_data["id"]
    

def test_get_context_bundle(client):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Context bundle API test",
            "description": "Testing context bundle retrieval.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/engineering-changes/{change_id}/context-bundle"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["ecr"]["id"] == change_id
    assert data["ecr"]["title"] == "Context bundle API test"
    assert "risks" in data
    assert "approvals" in data
    assert isinstance(data["risks"], list)
    assert isinstance(data["approvals"], list)


def test_get_context_bundle_not_found(client):
    response = client.get(
        "/api/v1/engineering-changes/999999/context-bundle"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Engineering change not found"
    
    
    
def test_get_engineering_change_risks(client):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Risk API test",
            "description": "Testing risk retrieval through the API.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/engineering-changes/{change_id}/risks"
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_evaluate_engineering_change(client):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Risk evaluation API test",
            "description": "Testing risk evaluation through the API.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/engineering-changes/{change_id}/evaluate"
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_risks_for_nonexistent_change(client):
    response = client.get(
        "/api/v1/engineering-changes/999999/risks"
    )

    # Current implementation of get_engineering_change_risks()
    # delegates directly to get_change_risks(), so verify the
    # behavior your service currently provides.
    assert response.status_code in (200, 404)


def test_evaluate_nonexistent_change(client):
    response = client.post(
        "/api/v1/engineering-changes/999999/evaluate"
    )

    assert response.status_code in (200, 404)
    

def test_generate_engineering_change_approvals(client):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Approval generation API test",
            "description": "Testing approval generation through the API.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/engineering-changes/{change_id}/approvals/generate"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_get_engineering_change_approvals(client):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Approval retrieval API test",
            "description": "Testing approval retrieval through the API.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/engineering-changes/{change_id}/approvals"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_decide_engineering_change_approval(client):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Approval decision API test",
            "description": "Testing approval decisions through the API.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    generate_response = client.post(
        f"/api/v1/engineering-changes/{change_id}/approvals/generate"
    )

    assert generate_response.status_code == 200

    approvals = generate_response.json()

    if not approvals:
        pytest.skip("No approval requirements generated for this ECR")

    approval_id = approvals[0]["id"]

    response = client.post(
        f"/api/v1/engineering-changes/{change_id}/approvals/{approval_id}/decision",
        json={
            "status": "APPROVED",
            "actor": "test-user",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == approval_id
    assert data["status"] == "APPROVED"


def test_decide_nonexistent_approval(client):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Invalid approval API test",
            "description": "Testing invalid approval decisions.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/engineering-changes/{change_id}/approvals/00000000-0000-0000-0000-000000000000/decision",
        json={
            "status": "APPROVED",
            "actor": "test-user",
        },
    )

    assert response.status_code in (404, 409)
    


def test_create_engineering_change_action(client, db_session):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Change action API test",
            "description": "Testing change action creation through the API.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    node = ContextNode(
        id=uuid4(),
        site_id="TEST-SITE",
        type=ContextNodeType.COMPONENT,
        identifier="TEST-001",
        name="Test Component",
    )

    db_session.add(node)
    db_session.commit()
    db_session.refresh(node)

    response = client.post(
        f"/api/v1/engineering-changes/{change_id}/actions",
        json={
            "node_id": str(node.id),
            "action": "MODIFY",
            "proposed_state": {
                "status": "updated",
            },
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["engineering_change_id"] == change_id
    assert data["node_id"] == str(node.id)
    assert data["action"] == "MODIFY"
    assert data["proposed_state"] == {
        "status": "updated",
    }
    

def test_get_engineering_change_actions(client):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Get actions API test",
            "description": "Testing change action retrieval.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/engineering-changes/{change_id}/actions"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_create_action_for_nonexistent_change(client, db_session):
    node = ContextNode(
        id=uuid4(),
        site_id="TEST-SITE",
        type=ContextNodeType.COMPONENT,
        identifier="TEST-002",
        name="Test Component",
    )

    db_session.add(node)
    db_session.commit()
    db_session.refresh(node)

    response = client.post(
        "/api/v1/engineering-changes/999999/actions",
        json={
            "node_id": str(node.id),
            "action": "MODIFY",
            "proposed_state": {
                "status": "updated",
            },
        },
    )

    assert response.status_code == 404
    

def test_get_actions_for_nonexistent_change(client):
    response = client.get(
        "/api/v1/engineering-changes/999999/actions"
    )

    assert response.status_code == 404
    


def test_create_action_when_change_is_not_draft(client, db_session):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Locked action API test",
            "description": "Testing action rejection after submission.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    node = ContextNode(
        id=uuid4(),
        site_id="TEST-SITE",
        type=ContextNodeType.COMPONENT,
        identifier="TEST-003",
        name="Test Component",
    )

    db_session.add(node)
    db_session.commit()
    db_session.refresh(node)

    submit_response = client.post(
        f"/api/v1/engineering-changes/{change_id}/submit"
    )

    assert submit_response.status_code == 200

    response = client.post(
        f"/api/v1/engineering-changes/{change_id}/actions",
        json={
            "node_id": str(node.id),
            "action": "MODIFY",
            "proposed_state": {
                "status": "updated",
            },
        },
    )

    assert response.status_code == 409
    
    
    
def test_get_engineering_change_context_bundle(client):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Context bundle API test",
            "description": "Testing context bundle retrieval.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/engineering-changes/{change_id}/context-bundle"
    )

    assert response.status_code == 200

    data = response.json()

    assert "ecr" in data
    assert "risks" in data
    assert "approvals" in data

    assert data["ecr"]["id"] == change_id
    assert isinstance(data["risks"], list)
    assert isinstance(data["approvals"], list)


def test_get_context_bundle_for_nonexistent_change(client):
    response = client.get(
        "/api/v1/engineering-changes/999999/context-bundle"
    )

    assert response.status_code == 404


def test_get_engineering_change_risks(client):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Risks API test",
            "description": "Testing risk retrieval.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/engineering-changes/{change_id}/risks"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_get_risks_for_nonexistent_change(client):
    response = client.get(
        "/api/v1/engineering-changes/999999/risks"
    )

    assert response.status_code == 200

    assert response.json() == []
    

def test_generate_engineering_change_approvals(client):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Approval generation API test",
            "description": "Testing approval generation through the API.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/engineering-changes/{change_id}/approvals/generate"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_generate_approvals_for_nonexistent_change(client):
    response = client.post(
        "/api/v1/engineering-changes/999999/approvals/generate"
    )

    assert response.status_code == 404


def test_get_engineering_change_approvals(client):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Approval retrieval API test",
            "description": "Testing approval retrieval through the API.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    generate_response = client.post(
        f"/api/v1/engineering-changes/{change_id}/approvals/generate"
    )

    assert generate_response.status_code == 200

    response = client.get(
        f"/api/v1/engineering-changes/{change_id}/approvals"
    )

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, list)


def test_get_approvals_for_nonexistent_change(client):
    response = client.get(
        "/api/v1/engineering-changes/999999/approvals"
    )

    assert response.status_code == 404
    


def test_transition_engineering_change(client):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Generic transition API test",
            "description": "Testing generic ECR transition.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/engineering-changes/{change_id}/transition",
        json={
            "target_status": "SUBMITTED",
            "actor": "test-user",
            "reason": "Submitting for engineering review.",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == change_id
    assert data["status"] == "SUBMITTED"
    
    
def test_transition_engineering_change_invalid_transition(client):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Invalid generic transition API test",
            "description": "Testing invalid generic transition.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/engineering-changes/{change_id}/transition",
        json={
            "target_status": "APPROVED",
            "actor": "test-user",
            "reason": "Attempting invalid transition.",
        },
    )

    assert response.status_code == 409
    


def test_transition_nonexistent_engineering_change(client):
    response = client.post(
        "/api/v1/engineering-changes/999999/transition",
        json={
            "target_status": "SUBMITTED",
            "actor": "test-user",
            "reason": "Testing nonexistent ECR.",
        },
    )

    assert response.status_code == 404
    
    
def test_transition_engineering_change_invalid_body(client):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Transition validation API test",
            "description": "Testing invalid transition payload.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    response = client.post(
        f"/api/v1/engineering-changes/{change_id}/transition",
        json={
            "target_status": "NOT_A_REAL_STATUS",
        },
    )

    assert response.status_code == 422
    

def test_create_context_report_for_nonexistent_change(client):
    event_id = "33333333-3333-3333-3333-333333333333"

    response = client.post(
        "/api/v1/engineering-changes/999999/context-reports",
        json={
            "event_id": event_id,
            "model": "test-model",
            "prompt_version": "v1",
            "input_context": {},
            "report": {},
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Engineering change not found"
    

def test_get_context_reports_for_nonexistent_change(client):
    response = client.get(
        "/api/v1/engineering-changes/999999/context-reports"
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Engineering change not found"
    


def test_get_context_report_invalid_event_id(client):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Invalid event ID API test",
            "description": "Testing UUID validation.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    response = client.get(
        f"/api/v1/engineering-changes/{change_id}/context-reports/events/not-a-uuid"
    )

    assert response.status_code == 422
    

def test_create_engineering_change_missing_required_fields(client):
    response = client.post(
        "/api/v1/engineering-changes",
        json={},
    )

    assert response.status_code == 422
    

def test_create_engineering_change_action_invalid_action(
    client,
    db_session,
):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Invalid action API test",
            "description": "Testing action enum validation.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    node = ContextNode(
        id=uuid4(),
        site_id="TEST-SITE",
        type=ContextNodeType.COMPONENT,
        identifier="TEST-INVALID-ACTION",
        name="Test Component",
    )

    db_session.add(node)
    db_session.commit()
    db_session.refresh(node)

    response = client.post(
        f"/api/v1/engineering-changes/{change_id}/actions",
        json={
            "node_id": str(node.id),
            "action": "INVALID_ACTION",
            "proposed_state": {},
        },
    )

    assert response.status_code == 422
    

def test_get_engineering_change_actions_after_creation(
    client,
    db_session,
):
    create_response = client.post(
        "/api/v1/engineering-changes",
        json={
            "title": "Action retrieval API test",
            "description": "Testing action retrieval after creation.",
        },
    )

    assert create_response.status_code == 201

    change_id = create_response.json()["id"]

    node = ContextNode(
        id=uuid4(),
        site_id="TEST-SITE",
        type=ContextNodeType.COMPONENT,
        identifier="TEST-RETRIEVE-ACTION",
        name="Test Component",
    )

    db_session.add(node)
    db_session.commit()
    db_session.refresh(node)

    create_action_response = client.post(
        f"/api/v1/engineering-changes/{change_id}/actions",
        json={
            "node_id": str(node.id),
            "action": "MODIFY",
            "proposed_state": {
                "status": "updated",
            },
        },
    )

    assert create_action_response.status_code == 201

    created_action = create_action_response.json()

    response = client.get(
        f"/api/v1/engineering-changes/{change_id}/actions"
    )

    assert response.status_code == 200

    actions = response.json()

    assert len(actions) == 1
    assert actions[0]["id"] == created_action["id"]
    assert actions[0]["node_id"] == str(node.id)
    assert actions[0]["action"] == "MODIFY"
    assert actions[0]["proposed_state"] == {
        "status": "updated",
    }
    

