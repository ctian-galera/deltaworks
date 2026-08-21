import pytest

from app.models.engineering_change import ChangeStatus
from app.workflows.engineering_change import (
    InvalidChangeTransition,
    transition,
)


def test_valid_transition():
    result = transition(
        ChangeStatus.DRAFT,
        ChangeStatus.SUBMITTED,
    )

    assert result == ChangeStatus.SUBMITTED


def test_rejection_path():
    result = transition(
        ChangeStatus.UNDER_REVIEW,
        ChangeStatus.REJECTED,
    )

    assert result == ChangeStatus.REJECTED


def test_invalid_transition():
    with pytest.raises(InvalidChangeTransition):
        transition(
            ChangeStatus.DRAFT,
            ChangeStatus.APPROVED,
        )


def test_closed_is_terminal():
    with pytest.raises(InvalidChangeTransition):
        transition(
            ChangeStatus.CLOSED,
            ChangeStatus.DRAFT,
        )