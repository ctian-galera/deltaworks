import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class RiskCategory(str, Enum):
    SAFETY = "SAFETY"
    CONTROLS = "CONTROLS"
    PRODUCTION = "PRODUCTION"
    COMPLIANCE = "COMPLIANCE"


class RiskSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class RiskFinding(Base):
    __tablename__ = "risk_findings"

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

    node_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("context_nodes.id"),
        nullable=False,
        index=True,
    )

    category: Mapped[RiskCategory] = mapped_column(
        SQLEnum(RiskCategory),
        nullable=False,
    )

    severity: Mapped[RiskSeverity] = mapped_column(
        SQLEnum(RiskSeverity),
        nullable=False,
    )

    reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )