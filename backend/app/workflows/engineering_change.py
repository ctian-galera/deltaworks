from app.models.engineering_change import ChangeStatus


ALLOWED_TRANSITIONS: dict[ChangeStatus, set[ChangeStatus]] = {
    ChangeStatus.DRAFT: {
        ChangeStatus.SUBMITTED,
    },
    ChangeStatus.SUBMITTED: {
        ChangeStatus.UNDER_REVIEW,
    },
    ChangeStatus.UNDER_REVIEW: {
        ChangeStatus.APPROVED,
        ChangeStatus.REJECTED,
    },
    ChangeStatus.APPROVED: {
        ChangeStatus.IMPLEMENTING,
    },
    ChangeStatus.IMPLEMENTING: {
        ChangeStatus.VERIFIED,
    },
    ChangeStatus.VERIFIED: {
        ChangeStatus.CLOSED,
    },
    ChangeStatus.REJECTED: {
        ChangeStatus.DRAFT,
    },
    ChangeStatus.CLOSED: set(),
}


class InvalidChangeTransition(Exception):
    """Raised when an engineering change attempts an invalid transition."""


def transition(
    current: ChangeStatus,
    target: ChangeStatus,
) -> ChangeStatus:
    allowed = ALLOWED_TRANSITIONS.get(current, set())

    if target not in allowed:
        raise InvalidChangeTransition(
            f"Invalid engineering change transition: "
            f"{current.value} -> {target.value}"
        )

    return target