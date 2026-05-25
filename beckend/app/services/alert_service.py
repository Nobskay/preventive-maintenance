"""
Alert service - alert generation and management
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.models.alert import Alert
from app.models.component import Component
from app.models.runtime import Runtime
from app.schemas.alert import AlertCreate, AlertResolve


def get_alerts(
    db: Session,
    machine_id: Optional[int] = None,
    active_only: bool = False,
    severity: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Alert]:
    query = db.query(Alert)
    if machine_id:
        query = query.filter(Alert.machine_id == machine_id)
    if active_only:
        query = query.filter(Alert.is_active == True)
    if severity:
        query = query.filter(Alert.alert_severity == severity)
    return query.order_by(Alert.created_at.desc()).offset(skip).limit(limit).all()


def get_alert(db: Session, alert_id: int) -> Optional[Alert]:
    return db.query(Alert).filter(Alert.alert_id == alert_id).first()


def create_alert(db: Session, data: AlertCreate) -> Alert:
    alert = Alert(
        machine_id=data.machine_id,
        component_id=data.component_id,
        alert_type=data.alert_type,
        alert_severity=data.alert_severity,
        message=data.message,
        additional_data=data.additional_data,
        created_at=datetime.utcnow(),
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def resolve_alert(db: Session, alert_id: int, data: AlertResolve, user_id: Optional[int] = None) -> Optional[Alert]:
    alert = get_alert(db, alert_id)
    if not alert:
        return None
    alert.resolved_at = datetime.utcnow()
    alert.resolved_by = user_id
    alert.resolution_notes = data.resolution_notes
    alert.is_active = False
    db.commit()
    db.refresh(alert)
    return alert


def get_active_alert_count(db: Session, machine_id: Optional[int] = None) -> int:
    query = db.query(func.count(Alert.alert_id)).filter(Alert.is_active == True)
    if machine_id:
        query = query.filter(Alert.machine_id == machine_id)
    return query.scalar()


def get_alert_counts_by_severity(db: Session) -> dict:
    results = (
        db.query(Alert.alert_severity, func.count(Alert.alert_id))
        .filter(Alert.is_active == True)
        .group_by(Alert.alert_severity)
        .all()
    )
    return {severity: count for severity, count in results}


def generate_maintenance_alerts(db: Session) -> List[Alert]:
    """Scan all components and generate alerts for those needing maintenance"""
    from app.services.machine_service import _calculate_component_health

    generated = []
    components = db.query(Component).all()

    for comp in components:
        latest_runtime = (
            db.query(Runtime)
            .filter(Runtime.machine_id == comp.machine_id)
            .order_by(Runtime.timestamp.desc())
            .first()
        )
        current_hours = float(latest_runtime.runtime_hours) if latest_runtime else 0
        health = _calculate_component_health(comp, current_hours, db)

        # Check if alert already exists for this component
        existing = (
            db.query(Alert)
            .filter(
                Alert.component_id == comp.component_id,
                Alert.is_active == True,
                Alert.alert_type.in_(["WARNING", "CRITICAL", "MAINTENANCE_DUE"]),
            )
            .first()
        )

        if health["health_status"] == "CRITICAL" and not existing:
            alert = create_alert(
                db,
                AlertCreate(
                    machine_id=comp.machine_id,
                    component_id=comp.component_id,
                    alert_type="CRITICAL",
                    alert_severity="critical",
                    message=f"Component '{comp.component_name}' has consumed {health['life_consumed_percent']}% of its rated life. Immediate replacement recommended.",
                    additional_data={
                        "health_percent": health["health_percent"],
                        "life_consumed_percent": health["life_consumed_percent"],
                        "remaining_hours": health["remaining_useful_life_hours"],
                    },
                ),
            )
            generated.append(alert)

        elif health["health_status"] == "WARNING" and not existing:
            alert = create_alert(
                db,
                AlertCreate(
                    machine_id=comp.machine_id,
                    component_id=comp.component_id,
                    alert_type="WARNING",
                    alert_severity="warning",
                    message=f"Component '{comp.component_name}' has consumed {health['life_consumed_percent']}% of its rated life. Schedule maintenance soon.",
                    additional_data={
                        "health_percent": health["health_percent"],
                        "life_consumed_percent": health["life_consumed_percent"],
                        "remaining_hours": health["remaining_useful_life_hours"],
                    },
                ),
            )
            generated.append(alert)

    return generated
