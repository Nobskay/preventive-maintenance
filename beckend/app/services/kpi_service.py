"""
KPI Service - Industrial reliability metrics calculations
MTBF, MTTR, Availability, Failure Frequency
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from datetime import datetime, timedelta

from app.models.machine import Machine
from app.models.downtime import Downtime
from app.models.runtime import Runtime


def _duration_hours(duration) -> float:
    """Convert a Python timedelta-like value to hours."""
    if not duration:
        return 0.0
    if hasattr(duration, "total_seconds"):
        return duration.total_seconds() / 3600
    return float(duration)


def calculate_machine_kpi(db: Session, machine_id: int, days: int = 90) -> dict:
    """Calculate KPIs for a specific machine"""
    cutoff = datetime.utcnow() - timedelta(days=days)

    # Get unplanned downtime events
    failures = (
        db.query(Downtime)
        .filter(
            Downtime.machine_id == machine_id,
            Downtime.is_unplanned == True,
            Downtime.timestamp_start >= cutoff,
        )
        .all()
    )

    total_failures = len(failures)
    total_downtime_hours = sum(_duration_hours(d.downtime_duration) for d in failures)

    # Get total runtime
    runtime_records = (
        db.query(Runtime)
        .filter(Runtime.machine_id == machine_id, Runtime.timestamp >= cutoff)
        .order_by(Runtime.timestamp.asc())
        .all()
    )

    if runtime_records:
        delta_sum = sum(float(record.delta_hours or 0) for record in runtime_records)
        if delta_sum > 0:
            total_uptime_hours = delta_sum
        else:
            total_uptime_hours = float(runtime_records[-1].runtime_hours) - float(runtime_records[0].runtime_hours)
    else:
        total_uptime_hours = 0

    # MTBF = Total Uptime / Number of Failures
    mtbf = total_uptime_hours / total_failures if total_failures > 0 else None

    # MTTR = Total Downtime / Number of Failures
    mttr = total_downtime_hours / total_failures if total_failures > 0 else None

    # Availability = Uptime / (Uptime + Downtime) * 100
    total_time = total_uptime_hours + total_downtime_hours
    availability = (total_uptime_hours / total_time * 100) if total_time > 0 else 100.0

    # Failure Frequency = Failures per week
    weeks = days / 7
    failure_frequency = total_failures / weeks if weeks > 0 else 0

    return {
        "machine_id": machine_id,
        "mtbf_hours": round(mtbf, 2) if mtbf else None,
        "mttr_hours": round(mttr, 2) if mttr else None,
        "availability_percent": round(availability, 2),
        "failure_frequency": round(failure_frequency, 4),
        "total_failures": total_failures,
        "total_uptime_hours": round(total_uptime_hours, 2),
        "total_downtime_hours": round(total_downtime_hours, 2),
        "period_days": days,
    }


def calculate_all_machine_kpis(db: Session, days: int = 90) -> List[dict]:
    """Calculate KPIs for all machines"""
    machines = db.query(Machine).all()
    kpis = []
    for machine in machines:
        kpi = calculate_machine_kpi(db, machine.machine_id, days)
        kpi["machine_name"] = machine.machine_name
        kpis.append(kpi)
    return kpis


def get_dashboard_summary(db: Session) -> dict:
    """Get aggregated dashboard summary"""
    from app.models.alert import Alert
    from app.models.component import Component
    from app.models.recommendation import MaintenanceRecommendation

    total_machines = db.query(func.count(Machine.machine_id)).scalar()
    active_machines = db.query(func.count(Machine.machine_id)).filter(Machine.status == "active").scalar()
    maintenance_machines = db.query(func.count(Machine.machine_id)).filter(Machine.status == "maintenance").scalar()
    total_components = db.query(func.count(Component.component_id)).scalar()

    active_alerts = db.query(func.count(Alert.alert_id)).filter(Alert.is_active == True).scalar()
    critical_alerts = (
        db.query(func.count(Alert.alert_id))
        .filter(Alert.is_active == True, Alert.alert_severity == "critical")
        .scalar()
    )
    warning_alerts = (
        db.query(func.count(Alert.alert_id))
        .filter(Alert.is_active == True, Alert.alert_severity == "warning")
        .scalar()
    )

    overdue_recommendations = (
        db.query(func.count(MaintenanceRecommendation.recommendation_id))
        .filter(MaintenanceRecommendation.status == "open")
        .scalar()
    )

    # Calculate averages across all machines
    all_kpis = calculate_all_machine_kpis(db, days=90)
    avg_availability = (
        sum(k["availability_percent"] for k in all_kpis) / len(all_kpis) if all_kpis else 0
    )
    mtbf_values = [k["mtbf_hours"] for k in all_kpis if k["mtbf_hours"] is not None]
    mttr_values = [k["mttr_hours"] for k in all_kpis if k["mttr_hours"] is not None]
    avg_mtbf = sum(mtbf_values) / len(mtbf_values) if mtbf_values else 0
    avg_mttr = sum(mttr_values) / len(mttr_values) if mttr_values else 0

    return {
        "total_machines": total_machines,
        "active_machines": active_machines,
        "machines_in_maintenance": maintenance_machines,
        "total_components": total_components,
        "active_alerts": active_alerts,
        "critical_alerts": critical_alerts,
        "warning_alerts": warning_alerts,
        "avg_availability": round(avg_availability, 2),
        "avg_mtbf": round(avg_mtbf, 2),
        "avg_mttr": round(avg_mttr, 2),
        "overdue_recommendations": overdue_recommendations,
    }
