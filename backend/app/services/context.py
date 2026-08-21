from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.context_edge import ContextEdge
from app.models.context_node import ContextNode
from app.schemas.context import ContextEdgeCreate, ContextNodeCreate


def create_node(
    db: Session,
    data: ContextNodeCreate,
) -> ContextNode:
    node = ContextNode(
        site_id=data.site_id,
        type=data.type,
        identifier=data.identifier,
        name=data.name,
        metadata_json=data.metadata,
    )

    db.add(node)
    db.commit()
    db.refresh(node)

    return node


def get_node(
    db: Session,
    node_id: UUID,
) -> ContextNode | None:
    return db.get(ContextNode, node_id)


def create_edge(
    db: Session,
    data: ContextEdgeCreate,
) -> ContextEdge:
    edge = ContextEdge(
        parent_id=data.parent_id,
        child_id=data.child_id,
        relationship_type=data.relationship_type,
        metadata_json=data.metadata
    )

    db.add(edge)
    db.commit()
    db.refresh(edge)

    return edge


def get_node_edges(
    db: Session,
    node_id: UUID,
) -> list[ContextEdge]:
    statement = select(ContextEdge).where(
        (ContextEdge.parent_id == node_id)
        | (ContextEdge.child_id == node_id)
    )

    return list(db.scalars(statement).all())