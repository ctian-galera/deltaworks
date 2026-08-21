import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ApprovalRole(str, Enum):
    SAFETY_BOARD = "SAFETY_BOARD"
    CONTROLS_ENGINEER = "CONTROLS_ENGINEER"
    PLANT_MANAGER = "PLANT_MANAGER"
    COMPLIANCE_ENGINEER = "COMPLIANCE_ENGINEER"


class ApprovalStatus(str, Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"


class ApprovalRequirement(Base):
    __tablename__ = "approval_requirements"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    engineering_change_id: Mapped[int] = mapped_column(
        ForeignKey("engineering_changes.id"),
        nullable=False,
        index=True,
    )

    role: Mapped[ApprovalRole] = mapped_column(
        SQLEnum(ApprovalRole),
        nullable=False,
    )

    status: Mapped[ApprovalStatus] = mapped_column(
        SQLEnum(ApprovalStatus),
        nullable=False,
        default=ApprovalStatus.PENDING,
    )

    actor: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    acted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )