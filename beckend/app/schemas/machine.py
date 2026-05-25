"""
Machine schemas for request/response validation
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from enum import Enum


class MachineType(str, Enum):
    AGV = "AGV"
    ROBOTIC_ARM = "Robotic Arm"
    CONVEYOR = "Conveyor"
    CNC = "CNC"
    COMPRESSOR = "Compressor"
    MOTOR = "Motor"
    PUMP = "Pump"
    FAN = "Fan"
    LATHE = "Lathe"
    DRILL = "Drill"
    OTHER = "Other"


class MachineStatus(str, Enum):
    ACTIVE = "active"
    IDLE = "idle"
    MAINTENANCE = "maintenance"
    DECOMMISSIONED = "decommissioned"


class OperatingSchedule(str, Enum):
    CONTINUOUS = "continuous"
    SHIFT = "shift"
    PART_TIME = "part-time"


class MachineBase(BaseModel):
    machine_name: str = Field(..., min_length=1, max_length=255)
    machine_type: MachineType
    manufacturer: Optional[str] = None
    installation_date: date
    operating_schedule: OperatingSchedule = OperatingSchedule.CONTINUOUS
    status: MachineStatus = MachineStatus.ACTIVE
    notes: Optional[str] = None


class MachineCreate(MachineBase):
    pass


class MachineUpdate(BaseModel):
    machine_name: Optional[str] = Field(None, min_length=1, max_length=255)
    machine_type: Optional[MachineType] = None
    manufacturer: Optional[str] = None
    installation_date: Optional[date] = None
    operating_schedule: Optional[OperatingSchedule] = None
    status: Optional[MachineStatus] = None
    notes: Optional[str] = None


class MachineResponse(MachineBase):
    machine_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MachineWithHealth(MachineResponse):
    overall_health_percent: Optional[float] = None
    overall_health_status: Optional[str] = None
    active_alerts: int = 0
    component_count: int = 0
