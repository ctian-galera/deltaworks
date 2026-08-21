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
        WITH RECURSIVE impact_tree AS (
            SELECT
                id AS node_id,
                0 AS depth,
                NULL::text AS relationship_type,
                ARRAY[id] AS path
            FROM context_nodes
            WHERE id = :root_node_id

            UNION ALL

            SELECT
                CASE
                    WHEN e.parent_id = it.node_id
                    THEN e.child_id
                    ELSE e.parent_id
                END AS node_id,

                it.depth + 1 AS depth,

                e.relationship_type::text AS relationship_type,

                it.path ||
                CASE
                    WHEN e.parent_id = it.node_id
                    THEN e.child_id
                    ELSE e.parent_id
                END AS path

            FROM impact_tree it
            JOIN context_edges e
                ON e.parent_id = it.node_id
                OR e.child_id = it.node_id

            WHERE it.depth < :max_depth

              AND NOT (
                  CASE
                      WHEN e.parent_id = it.node_id
                      THEN e.child_id
                      ELSE e.parent_id
                  END = ANY(it.path)
              )
        )

        SELECT
            n.id AS node_id,
            n.identifier,
            n.name,
            it.relationship_type,
            it.depth

        FROM impact_tree it
        JOIN context_nodes n
            ON n.id = it.node_id

        WHERE it.depth > 0

        ORDER BY it.depth, n.identifier
        """
    )

    result = db.execute(
        query,
        {
            "root_node_id": node_id,
            "max_depth": max_depth,
        },
    )

    return [
        {
            "node_id": row.node_id,
            "identifier": row.identifier,
            "name": row.name,
            "relationship_type": row.relationship_type,
            "depth": row.depth,
        }
        for row in result
    ]
    
    
def get_impact_context(
    db: Session,
    node_id: UUID,
    max_depth: int = 3,
) -> list[dict]:
    query = text(
        """
        WITH RECURSIVE impact_tree AS (
            SELECT
                id AS node_id,
                0 AS depth,
                NULL::text AS relationship_type,
                ARRAY[id] AS path
            FROM context_nodes
            WHERE id = :root_node_id

            UNION ALL

            SELECT
                CASE
                    WHEN e.parent_id = it.node_id
                    THEN e.child_id
                    ELSE e.parent_id
                END AS node_id,

                it.depth + 1 AS depth,

                e.relationship_type::text AS relationship_type,

                it.path ||
                CASE
                    WHEN e.parent_id = it.node_id
                    THEN e.child_id
                    ELSE e.parent_id
                END AS path

            FROM impact_tree it
            JOIN context_edges e
                ON e.parent_id = it.node_id
                OR e.child_id = it.node_id

            WHERE it.depth < :max_depth

              AND NOT (
                  CASE
                      WHEN e.parent_id = it.node_id
                      THEN e.child_id
                      ELSE e.parent_id
                  END = ANY(it.path)
              )
        )

        SELECT
            n.id AS node_id,
            n.identifier,
            n.name,
            n.type::text AS node_type,
            n.metadata,
            it.relationship_type,
            it.depth

        FROM impact_tree it
        JOIN context_nodes n
            ON n.id = it.node_id

        WHERE it.depth > 0

        ORDER BY it.depth, n.identifier
        """
    )

    result = db.execute(
        query,
        {
            "root_node_id": node_id,
            "max_depth": max_depth,
        },
    )

    return [
        {
            "node_id": row.node_id,
            "identifier": row.identifier,
            "name": row.name,
            "node_type": row.node_type,
            "metadata": row.metadata or {},
            "relationship_type": row.relationship_type,
            "depth": row.depth,
        }
        for row in result
    ]