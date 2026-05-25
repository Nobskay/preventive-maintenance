"""
Maintenance Recommendation schemas
"""
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional
from decimal import Decimal
from enum import Enum


class RecommendationType(str, Enum):
    REPLACEMENT = "replacement"
    INSPECTION = "inspection"
    LUBRICATION = "lubrication"
    REPAIR = "repair"
    ADJUSTMENT = "adjustment"
    CLEANING = "cleaning"


class Urgency(str, Enum):
    IMMEDIATE = "immediate"
    URGENT = "urgent"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RecommendationStatus(str, Enum):
    OPEN = "open"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class RecommendationBase(BaseModel):
    machine_id: int
    component_id: Optional[int] = None
    recommendation_type: RecommendationType
    description: str
    urgency: Urgency = Urgency.MEDIUM
    estimated_cost: Optional[Decimal] = Field(None, ge=0)
    estimated_duration_hours: Optional[Decimal] = Field(None, gt=0)


class RecommendationCreate(RecommendationBase):
    pass


class RecommendationUpdate(BaseModel):
    status: Optional[RecommendationStatus] = None
    scheduled_date: Optional[date] = None
    urgency: Optional[Urgency] = None


class RecommendationResponse(RecommendationBase):
    recommendation_id: int
    recommended_by_system: str
    status: str
    scheduled_date: Optional[date] = None
    completed_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
