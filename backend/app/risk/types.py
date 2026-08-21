from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class RiskCategory(str, Enum):
    SAFETY = "SAFETY"
    CONTROLS = "CONTROLS"
    PRODUCTION = "PRODUCTION"
    COMPLIANCE = "COMPLIANCE"


class RiskSeverity(str, Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class RiskFinding:
    category: RiskCategory
    severity: RiskSeverity
    reason: str
    node_id: UUID