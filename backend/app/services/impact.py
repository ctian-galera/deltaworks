from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.orm import Session

from app.services.context import get_impact


@dataclass
class ImpactedNode:
    node_id: UUID
    identifier: str
    name: str
    relationship_type: str
    depth: int


@dataclass
class ImpactAssessment:
    root_node_id: UUID
    impacted_nodes: list[ImpactedNode]
    total_impacted: int
    
def assess_impact(
    db: Session,
    root_node_id: UUID,
    max_depth: int = 3,
) -> ImpactAssessment:
    result = get_impact(
        db,
        root_node_id=root_node_id,
        max_depth=max_depth,
    )

    impacted_nodes = [
        ImpactedNode(
            node_id=item["node_id"],
            identifier=item["identifier"],
            name=item["name"],
            relationship_type=item["relationship_type"],
            depth=item["depth"],
        )
        for item in result
    ]

    return ImpactAssessment(
        root_node_id=root_node_id,
        impacted_nodes=impacted_nodes,
        total_impacted=len(impacted_nodes),
    )