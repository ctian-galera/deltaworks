from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.engineering_change import ChangeStatus


class EngineeringChangeCreate(BaseModel):
    title: str
    description: str


class EngineeringChangeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    change_number: str
    title: str
    description: str
    status: ChangeStatus
    created_at: datetime
    

class EngineeringChangeTransition(BaseModel):
    target_status: ChangeStatus
    actor: str = "system"
    reason: str | None = None