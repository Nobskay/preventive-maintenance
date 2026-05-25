"""
SQLAlchemy ORM Models for Predictive Maintenance System
"""
from app.models.machine import Machine
from app.models.component import Component
from app.models.runtime import Runtime
from app.models.downtime import Downtime
from app.models.alert import Alert
from app.models.recommendation import MaintenanceRecommendation
from app.models.kpi import KPISnapshot
from app.models.user import User
from app.models.maintenance import MaintenanceEvent

__all__ = [
    "Machine",
    "Component",
    "Runtime",
    "Downtime",
    "Alert",
    "MaintenanceRecommendation",
    "KPISnapshot",
    "User",
    "MaintenanceEvent",
]
