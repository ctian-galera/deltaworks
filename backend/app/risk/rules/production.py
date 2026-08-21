from app.risk.types import RiskCategory, RiskFinding, RiskSeverity


def evaluate_production(node, relationship_types):
    findings = []

    if "POWERED_BY" in relationship_types:
        findings.append(
            RiskFinding(
                category=RiskCategory.PRODUCTION,
                severity=RiskSeverity.WARNING,
                reason=(
                    f"Change may affect production equipment "
                    f"through power dependency involving "
                    f"{node.identifier}."
                ),
                node_id=node.id,
            )
        )

    return findings