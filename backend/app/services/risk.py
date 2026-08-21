from dataclasses import dataclass


@dataclass
class RiskFinding:
    category: str
    severity: str
    reason: str
    requires_approval: bool
    
def evaluate_node_risk(node) -> list[RiskFinding]:
    findings = []

    metadata = node.metadata or {}

    if metadata.get("safety_critical") is True:
        findings.append(
            RiskFinding(
                category="SAFETY",
                severity="HIGH",
                reason="Target node is marked safety-critical.",
                requires_approval=True,
            )
        )

    if metadata.get("production_critical") is True:
        findings.append(
            RiskFinding(
                category="PRODUCTION",
                severity="HIGH",
                reason="Target node is marked production-critical.",
                requires_approval=True,
            )
        )

    if metadata.get("electrical") is True:
        findings.append(
            RiskFinding(
                category="ELECTRICAL",
                severity="MEDIUM",
                reason="Change affects an electrical component.",
                requires_approval=False,
            )
        )

    return findings