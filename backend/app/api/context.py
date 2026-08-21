from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.context import (
    ContextEdgeCreate,
    ContextEdgeResponse,
    ContextNodeCreate,
    ContextNodeResponse,
    ImpactAnalysisResponse
)
from app.services.context import (
    create_edge,
    create_node,
    get_node,
    get_node_edges,
    get_impact
)

router = APIRouter(
    prefix="/context",
    tags=["Engineering Context"],
)


@router.post(
    "/nodes",
    response_model=ContextNodeResponse,
)
def create_context_node(
    data: ContextNodeCreate,
    db: Session = Depends(get_db),
):
    return create_node(db, data)


@router.get(
    "/nodes/{node_id}",
    response_model=ContextNodeResponse,
)
def read_context_node(
    node_id: UUID,
    db: Session = Depends(get_db),
):
    node = get_node(db, node_id)

    if node is None:
        raise HTTPException(
            status_code=404,
            detail="Context node not found",
        )

    return node


@router.post(
    "/edges",
    response_model=ContextEdgeResponse,
)
def create_context_edge(
    data: ContextEdgeCreate,
    db: Session = Depends(get_db),
):
    return create_edge(db, data)


@router.get(
    "/nodes/{node_id}/edges",
    response_model=list[ContextEdgeResponse],
)
def read_context_node_edges(
    node_id: UUID,
    db: Session = Depends(get_db),
):
    node = get_node(db, node_id)

    if node is None:
        raise HTTPException(
            status_code=404,
            detail="Context node not found",
        )

    return get_node_edges(db, node_id)


@router.get(
    "/nodes/{node_id}/impact",
    response_model=ImpactAnalysisResponse,
)
def get_node_impact(
    node_id: UUID,
    max_depth: int = Query(default=3, ge=1, le=10),
    db: Session = Depends(get_db),
):
    impact = get_impact(
        db=db,
        node_id=node_id,
        max_depth=max_depth,
    )

    if not impact:
        node_exists = db.execute(
            text(
                "SELECT 1 FROM context_nodes WHERE id = :node_id"
            ),
            {"node_id": node_id},
        ).first()

        if not node_exists:
            raise HTTPException(
                status_code=404,
                detail="Context node not found",
            )

    return {
        "root_node_id": node_id,
        "max_depth": max_depth,
        "impacted_nodes": impact,
    }