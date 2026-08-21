from app.models.approval_requirement import ApprovalRole
from app.models.risk_finding import RiskCategory, RiskSeverity


def map_risk_to_approval(
    category: RiskCategory,
    severity: RiskSeverity,
) -> ApprovalRole | None:

    if (
        category == RiskCategory.SAFETY
        and severity == RiskSeverity.CRITICAL
    ):
        return ApprovalRole.SAFETY_BOARD

    if category == RiskCategory.CONTROLS:
        return ApprovalRole.CONTROLS_ENGINEER

    if category == RiskCategory.PRODUCTION:
        return ApprovalRole.PLANT_MANAGER

    if category == RiskCategory.COMPLIANCE:
        return ApprovalRole.COMPLIANCE_ENGINEER

    return None