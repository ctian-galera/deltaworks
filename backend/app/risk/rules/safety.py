from app.risk.types import RiskCategory, RiskFinding, RiskSeverity


def evaluate_safety(node):
    findings = []

    if node.metadata_json.get("safety_critical") is True:
        findings.append(
            RiskFinding(
                category=RiskCategory.SAFETY,
                severity=RiskSeverity.CRITICAL,
                reason=(
                    f"Change affects safety-critical node "
                    f"{node.identifier}."
                ),
                node_id=node.id,
            )
        )

    return findings