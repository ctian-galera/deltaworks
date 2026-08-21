import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, Index, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ContextNodeType(str, Enum):
    SYSTEM = "SYSTEM"
    ASSET = "ASSET"
    COMPONENT = "COMPONENT"
    MATERIAL = "MATERIAL"
    DOCUMENT = "DOCUMENT"
    PROCESS = "PROCESS"


class ContextNode(Base):
    __tablename__ = "context_nodes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    site_id: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    type: Mapped[ContextNodeType] = mapped_column(
        SQLEnum(ContextNodeType),
        nullable=False,
    )

    identifier: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    metadata_json: Mapped[dict] = mapped_column(
        "metadata",
        JSONB,
        nullable=False,
        default=dict,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        Index(
            "uq_context_nodes_type_identifier",
            "type",
            "identifier",
            unique=True,
        ),
        Index(
            "ix_context_nodes_metadata",
            "metadata",
            postgresql_using="gin",
        ),
    )