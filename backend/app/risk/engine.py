from sqlalchemy.orm import Session

from app.models.context_node import ContextNode
from app.risk.rules.compliance import evaluate_compliance
from app.risk.rules.controls import evaluate_controls
from app.risk.rules.production import evaluate_production
from app.risk.rules.safety import evaluate_safety
from app.risk.types import RiskFinding
from app.services.context import get_impact_context

def evaluate_node(
    node: ContextNode,
    relationship_types: list[str] | None = None,
) -> list[RiskFinding]:
    relationship_types = relationship_types or []

    findings: list[RiskFinding] = []

    findings.extend(
        evaluate_safety(node)
    )

    findings.extend(
        evaluate_controls(
            node,
            relationship_types,
        )
    )

    findings.extend(
        evaluate_production(
            node,
            relationship_types,
        )
    )

    findings.extend(
        evaluate_compliance(node)
    )

    return findings


def evaluate_change(
    db: Session,
    engineering_change_id: int,
    max_depth: int = 3,
) -> list[RiskFinding]:
    from app.models.change_action import ChangeAction

    actions = list(
        db.query(ChangeAction)
        .filter(
            ChangeAction.engineering_change_id == engineering_change_id
        )
        .all()
    )

    findings: list[RiskFinding] = []

    for action in actions:
        impact = get_impact_context(
            db,
            action.node_id,
            max_depth=max_depth,
        )

        for item in impact:
            node = db.get(
                ContextNode,
                item["node_id"],
            )

            if node is None:
                continue

            relationship_types = []

            if item.get("relationship_type"):
                relationship_types.append(
                    item["relationship_type"]
                )

            findings.extend(
                evaluate_node(
                    node,
                    relationship_types,
                )
            )

    return findings