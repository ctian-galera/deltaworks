from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class EngineeringContextReportCreate(BaseModel):
    model: str = Field(
        min_length=1,
        max_length=100,
    )

    prompt_version: str = Field(
        min_length=1,
        max_length=50,
    )

    input_context: dict

    report: dict


class EngineeringContextReportResponse(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
    )

    id: UUID
    engineering_change_id: int
    model: str
    prompt_version: str
    input_context: dict
    report: dict
    created_at: datetime