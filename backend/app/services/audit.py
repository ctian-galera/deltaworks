from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent


def record_audit_event(
    db: Session,
    *,
    engineering_change_id: int,
    event_type: str,
    actor: str,
    from_status: str | None = None,
    to_status: str | None = None,
    reason: str | None = None,
) -> AuditEvent:
    event = AuditEvent(
        engineering_change_id=engineering_change_id,
        event_type=event_type,
        actor=actor,
        from_status=from_status,
        to_status=to_status,
        reason=reason,
    )

    db.add(event)

    return event