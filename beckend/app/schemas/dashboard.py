"""
Dashboard schemas for KPI and summary responses
"""
from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal


class KPIMetrics(BaseModel):
    machine_id: int
    machine_name: str
    mtbf_hours: Optional[float] = None
    mttr_hours: Optional[float] = None
    availability_percent: Optional[float] = None
    failure_frequency: Optional[float] = None
    total_failures: int = 0
    total_uptime_hours: float = 0
    total_downtime_hours: float = 0


class DashboardSummary(BaseModel):
    total_machines: int = 0
    active_machines: int = 0
    machines_in_maintenance: int = 0
    total_components: int = 0
    active_alerts: int = 0
    critical_alerts: int = 0
    warning_alerts: int = 0
    avg_availability: float = 0
    avg_mtbf: float = 0
    avg_mttr: float = 0
    overdue_recommendations: int = 0


class MachineHealthSummary(BaseModel):
    machine_id: int
    machine_name: str
    machine_type: str
    status: str
    overall_health_percent: float
    overall_health_status: str
    active_alerts: int = 0
    component_count: int = 0


class DowntimeTrend(BaseModel):
    date: str
    total_downtime_hours: float
    unplanned_downtime_hours: float
    failure_count: int


class FailureFrequency(BaseModel):
    machine_id: int
    machine_name: str
    failure_count: int
    period: str
