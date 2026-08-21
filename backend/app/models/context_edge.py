import uuid
from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class ContextRelationshipType(str, Enum):
    PART_OF = "PART_OF"
    CONTROLS = "CONTROLS"
    SENSES = "SENSES"
    POWERED_BY = "POWERED_BY"
    DESCRIBES = "DESCRIBES"
    GOVERNS = "GOVERNS"


class ContextEdge(Base):
    __tablename__ = "context_edges"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    parent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("context_nodes.id"),
        nullable=False,
    )

    child_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("context_nodes.id"),
        nullable=False,
    )

    relationship_type: Mapped[ContextRelationshipType] = mapped_column(
        SQLEnum(ContextRelationshipType),
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

    __table_args__ = (
        UniqueConstraint(
            "parent_id",
            "child_id",
            "relationship_type",
            name="uq_context_edge_relationship",
        ),
        Index("ix_context_edges_parent_id", "parent_id"),
        Index("ix_context_edges_child_id", "child_id"),
    )