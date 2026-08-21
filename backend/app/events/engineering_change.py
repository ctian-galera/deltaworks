from app.models.engineering_change import ChangeStatus


def build_status_changed_event(
    *,
    change_id: int,
    change_number: str,
    previous_status: ChangeStatus,
    new_status: ChangeStatus,
) -> dict:
    return {
        "event": "ecr.status_changed",
        "change_id": change_id,
        "change_number": change_number,
        "previous_status": previous_status.value,
        "new_status": new_status.value,
    }