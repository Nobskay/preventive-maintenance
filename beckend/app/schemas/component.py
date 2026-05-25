"""
Component schemas for request/response validation
"""
from enum import Enum
from pydantic import BaseModel, Field, model_validator
from datetime import date, datetime
from typing import Optional
from decimal import Decimal


class ComponentType(str, Enum):
    BEARING = "bearing"
    SEAL = "seal"
    BELT = "belt"
    CHAIN = "chain"
    MOTOR = "motor"
    PUMP = "pump"
    SENSOR = "sensor"
    VALVE = "valve"
    FILTER = "filter"
    HYDRAULIC = "hydraulic"
    PNEUMATIC = "pneumatic"
    OTHER = "other"


class ComponentBase(BaseModel):
    machine_id: int
    component_name: str = Field(..., min_length=1, max_length=255)
    component_type: ComponentType
    lifetime_hours: Optional[int] = Field(None, gt=0)
    lifetime_months: Optional[int] = Field(None, gt=0)
    installed_runtime_hours: Decimal = Field(default=Decimal("0"), ge=0)
    warning_threshold_percent: Decimal = Field(default=Decimal("90"), ge=0, le=100)
    critical_threshold_percent: Decimal = Field(default=Decimal("100"), ge=0, le=100)
    replacement_cost: Optional[Decimal] = Field(None, ge=0)
    maintenance_sop: Optional[str] = None
    installation_date: date
    last_replacement_date: Optional[date] = None

    @model_validator(mode="after")
    def validate_lifecycle_policy(self):
        if self.lifetime_hours is None and self.lifetime_months is None:
            raise ValueError("At least one lifecycle limit is required: lifetime_hours or lifetime_months")
        if self.warning_threshold_percent >= self.critical_threshold_percent:
            raise ValueError("warning_threshold_percent must be lower than critical_threshold_percent")
        return self


class ComponentCreate(ComponentBase):
    pass


class ComponentUpdate(BaseModel):
    component_name: Optional[str] = Field(None, min_length=1, max_length=255)
    component_type: Optional[ComponentType] = None
    lifetime_hours: Optional[int] = Field(None, gt=0)
    lifetime_months: Optional[int] = Field(None, gt=0)
    installed_runtime_hours: Optional[Decimal] = Field(None, ge=0)
    warning_threshold_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    critical_threshold_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    replacement_cost: Optional[Decimal] = Field(None, ge=0)
    maintenance_sop: Optional[str] = None
    installation_date: Optional[date] = None
    last_replacement_date: Optional[date] = None

    @model_validator(mode="after")
    def validate_threshold_update(self):
        if (
            self.warning_threshold_percent is not None
            and self.critical_threshold_percent is not None
            and self.warning_threshold_percent >= self.critical_threshold_percent
        ):
            raise ValueError("warning_threshold_percent must be lower than critical_threshold_percent")
        return self


class ComponentResponse(ComponentBase):
    component_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ComponentHealth(BaseModel):
    component_id: int
    component_name: str
    component_type: str
    health_percent: float
    life_consumed_percent: float
    health_status: str  # HEALTHY, WARNING, CRITICAL
    maintenance_due_status: str
    remaining_useful_life_hours: Optional[float] = None
    remaining_useful_life_days: Optional[float] = None
    current_runtime_hours: float = 0
    installed_runtime_hours: float = 0
    used_runtime_hours: float = 0
    lifetime_hours: Optional[int] = None
    lifetime_months: Optional[int] = None
    installation_date: date
    warning_threshold: float
    critical_threshold: float
