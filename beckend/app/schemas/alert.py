"""
Alert schemas for request/response validation
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any, Dict
from enum import Enum


class AlertType(str, Enum):
    MAINTENANCE_DUE = "MAINTENANCE_DUE"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"
    INFO = "INFO"
    FAILURE_PREDICTED = "FAILURE_PREDICTED"


class AlertSeverity(str, Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"


class AlertBase(BaseModel):
    machine_id: int
    component_id: Optional[int] = None
    alert_type: AlertType
    alert_severity: AlertSeverity = AlertSeverity.WARNING
    message: str
    additional_data: Optional[Dict[str, Any]] = None


class AlertCreate(AlertBase):
    pass


class AlertResolve(BaseModel):
    resolution_notes: Optional[str] = None


class AlertResponse(AlertBase):
    alert_id: int
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[int] = None
    resolution_notes: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True
