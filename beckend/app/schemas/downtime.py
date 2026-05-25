"""
Downtime schemas for request/response validation
"""
from pydantic import BaseModel, Field, field_serializer, model_validator
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum


class SeverityLevel(str, Enum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DowntimeBase(BaseModel):
    machine_id: int
    timestamp_start: datetime
    timestamp_end: datetime
    issue_description: str = Field(..., min_length=1)
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    severity_level: SeverityLevel = SeverityLevel.MEDIUM
    component_affected: Optional[int] = None
    is_unplanned: bool = True


class DowntimeCreate(DowntimeBase):
    @model_validator(mode="after")
    def validate_time_window(self):
        if self.timestamp_start >= self.timestamp_end:
            raise ValueError("timestamp_start must be before timestamp_end")
        return self


class DowntimeUpdate(BaseModel):
    timestamp_start: Optional[datetime] = None
    timestamp_end: Optional[datetime] = None
    issue_description: Optional[str] = Field(None, min_length=1)
    root_cause: Optional[str] = None
    corrective_action: Optional[str] = None
    severity_level: Optional[SeverityLevel] = None
    component_affected: Optional[int] = None
    is_unplanned: Optional[bool] = None

    @model_validator(mode="after")
    def validate_time_window(self):
        if (
            self.timestamp_start is not None
            and self.timestamp_end is not None
            and self.timestamp_start >= self.timestamp_end
        ):
            raise ValueError("timestamp_start must be before timestamp_end")
        return self


class DowntimeResponse(DowntimeBase):
    downtime_id: int
    downtime_duration: Optional[timedelta] = None
    created_at: datetime

    @field_serializer("downtime_duration")
    def serialize_duration(self, value: Optional[timedelta]):
        return str(value) if value else None

    class Config:
        from_attributes = True
