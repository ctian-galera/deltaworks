from app.risk.types import RiskCategory, RiskFinding, RiskSeverity


def evaluate_controls(node, relationship_types):
    findings = []

    if (
        node.type.value == "COMPONENT"
        and (
            "SENSES" in relationship_types
            or "CONTROLS" in relationship_types
        )
    ):
        findings.append(
            RiskFinding(
                category=RiskCategory.CONTROLS,
                severity=RiskSeverity.WARNING,
                reason=(
                    f"Change affects controls-related component "
                    f"{node.identifier}."
                ),
                node_id=node.id,
            )
        )

    return findings