from datetime import datetime, timezone
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ChangeActionType(str, Enum):
    ADD = "ADD"
    MODIFY = "MODIFY"
    REMOVE = "REMOVE"
    REPLACE = "REPLACE"


class ChangeAction(Base):
    __tablename__ = "change_actions"

    id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    engineering_change_id: Mapped[int] = mapped_column(
        ForeignKey("engineering_changes.id"),
        nullable=False,
        index=True,
    )

    node_id: Mapped[UUID] = mapped_column(
        ForeignKey("context_nodes.id"),
        nullable=False,
        index=True,
    )

    action: Mapped[ChangeActionType] = mapped_column(
        SQLEnum(ChangeActionType),
        nullable=False,
    )

    proposed_state: Mapped[dict] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )