from uuid import UUID

from sqlalchemy import select, text
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


def get_impact(
    db: Session,
    node_id: UUID,
    max_depth: int = 3,
):
    query = text(
        """
        WITH RECURSIVE impact AS (
            SELECT
                cn.id AS node_id,
                cn.identifier,
                cn.name,
                NULL::text AS relationship_type,
                0 AS depth,
                ARRAY[cn.id] AS path
            FROM context_nodes cn
            WHERE cn.id = :node_id

            UNION ALL

            SELECT
                parent.id AS node_id,
                parent.identifier,
                parent.name,
                ce.relationship_type::text AS relationship_type,
                i.depth + 1 AS depth,
                i.path || parent.id
            FROM impact i
            JOIN context_edges ce
                ON ce.child_id = i.node_id
            JOIN context_nodes parent
                ON parent.id = ce.parent_id
            WHERE i.depth < :max_depth
              AND NOT parent.id = ANY(i.path)
        )
        SELECT
            node_id,
            identifier,
            name,
            relationship_type,
            depth
        FROM impact
        WHERE depth > 0
        ORDER BY depth, identifier
        """
    )

    result = db.execute(
        query,
        {
            "node_id": node_id,
            "max_depth": max_depth,
        },
    )

    return result.mappings().all()