"""
Maintenance event schemas for work history and PM audit trail.
"""
from enum import Enum
from decimal import Decimal
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MaintenanceEventType(str, Enum):
    INSPECTION = "inspection"
    LUBRICATION = "lubrication"
    REPLACEMENT = "replacement"
    REPAIR = "repair"
    CALIBRATION = "calibration"
    CLEANING = "cleaning"


class MaintenanceTriggerSource(str, Enum):
    PREVENTIVE = "preventive"
    CORRECTIVE = "corrective"
    CONDITION_BASED = "condition_based"
    OPERATOR_REQUEST = "operator_request"
    SYSTEM_ALERT = "system_alert"


class MaintenanceEventBase(BaseModel):
    machine_id: int
    component_id: Optional[int] = None
    event_type: MaintenanceEventType
    trigger_source: MaintenanceTriggerSource = MaintenanceTriggerSource.PREVENTIVE
    work_order_code: Optional[str] = Field(None, max_length=100)
    performed_at: datetime
    duration_hours: Optional[Decimal] = Field(None, gt=0)
    technician: Optional[str] = Field(None, max_length=255)
    action_taken: str = Field(..., min_length=1)
    parts_replaced: Optional[str] = None
    notes: Optional[str] = None


class MaintenanceEventCreate(MaintenanceEventBase):
    pass


class MaintenanceEventUpdate(BaseModel):
    event_type: Optional[MaintenanceEventType] = None
    trigger_source: Optional[MaintenanceTriggerSource] = None
    work_order_code: Optional[str] = Field(None, max_length=100)
    performed_at: Optional[datetime] = None
    duration_hours: Optional[Decimal] = Field(None, gt=0)
    technician: Optional[str] = Field(None, max_length=255)
    action_taken: Optional[str] = Field(None, min_length=1)
    parts_replaced: Optional[str] = None
    notes: Optional[str] = None


class MaintenanceEventResponse(MaintenanceEventBase):
    maintenance_event_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
