from app.risk.types import RiskCategory, RiskFinding, RiskSeverity


def evaluate_compliance(node):
    findings = []

    if node.metadata_json.get("calibration_required") is True:
        findings.append(
            RiskFinding(
                category=RiskCategory.COMPLIANCE,
                severity=RiskSeverity.WARNING,
                reason=(
                    f"Change affects calibrated equipment "
                    f"{node.identifier}; calibration documentation "
                    f"may require review."
                ),
                node_id=node.id,
            )
        )

    return findings