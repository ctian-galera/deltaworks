from uuid import uuid4
from app.models.engineering_change import ChangeStatus


from uuid import UUID, uuid4


def build_status_changed_event(
    *,
    change_id: int,
    change_number: str,
    previous_status: ChangeStatus,
    new_status: ChangeStatus,
    event_id: UUID | None = None,
) -> dict:
    return {
        "event": "ecr.status_changed",
        "event_id": str(event_id or uuid4()),
        "change_id": change_id,
        "change_number": change_number,
        "previous_status": previous_status.value,
        "new_status": new_status.value,
    }