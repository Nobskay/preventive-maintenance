"""
Machine service - CRUD operations and business logic
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from app.models.machine import Machine
from app.models.component import Component
from app.models.runtime import Runtime
from app.models.alert import Alert
from app.schemas.machine import MachineCreate, MachineUpdate


def get_machines(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    machine_type: Optional[str] = None,
) -> List[Machine]:
    query = db.query(Machine)
    if status:
        query = query.filter(Machine.status == status)
    if machine_type:
        query = query.filter(Machine.machine_type == machine_type)
    return query.order_by(Machine.machine_name).offset(skip).limit(limit).all()


def get_machine(db: Session, machine_id: int) -> Optional[Machine]:
    return db.query(Machine).filter(Machine.machine_id == machine_id).first()


def create_machine(db: Session, data: MachineCreate) -> Machine:
    machine = Machine(**data.model_dump())
    db.add(machine)
    db.commit()
    db.refresh(machine)
    return machine


def update_machine(db: Session, machine_id: int, data: MachineUpdate) -> Optional[Machine]:
    machine = get_machine(db, machine_id)
    if not machine:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(machine, field, value)
    db.commit()
    db.refresh(machine)
    return machine


def delete_machine(db: Session, machine_id: int) -> bool:
    machine = get_machine(db, machine_id)
    if not machine:
        return False
    db.delete(machine)
    db.commit()
    return True


def get_machine_count(db: Session) -> int:
    return db.query(func.count(Machine.machine_id)).scalar()


def get_machine_health(db: Session, machine_id: int) -> dict:
    """Calculate overall machine health based on component health"""
    machine = get_machine(db, machine_id)
    if not machine:
        return None

    components = db.query(Component).filter(Component.machine_id == machine_id).all()
    if not components:
        return {
            "machine_id": machine_id,
            "machine_name": machine.machine_name,
            "overall_health_percent": 100.0,
            "overall_health_status": "HEALTHY",
            "components": [],
            "active_alerts": 0,
        }

    # Get latest runtime for the machine
    latest_runtime = (
        db.query(Runtime)
        .filter(Runtime.machine_id == machine_id)
        .order_by(Runtime.timestamp.desc())
        .first()
    )
    current_hours = float(latest_runtime.runtime_hours) if latest_runtime else 0

    component_healths = []
    for comp in components:
        health = _calculate_component_health(comp, current_hours, db)
        component_healths.append(health)

    overall_health = min(ch["health_percent"] for ch in component_healths) if component_healths else 100.0
    component_statuses = {ch["health_status"] for ch in component_healths}
    if "CRITICAL" in component_statuses:
        status = "CRITICAL"
    elif "WARNING" in component_statuses:
        status = "WARNING"
    else:
        status = "HEALTHY"

    active_alerts = (
        db.query(func.count(Alert.alert_id))
        .filter(Alert.machine_id == machine_id, Alert.is_active == True)
        .scalar()
    )

    return {
        "machine_id": machine_id,
        "machine_name": machine.machine_name,
        "overall_health_percent": round(overall_health, 2),
        "overall_health_status": status,
        "components": component_healths,
        "active_alerts": active_alerts,
    }


def _calculate_component_health(component, current_runtime_hours: float, db: Session) -> dict:
    """Calculate health for a single component"""
    from datetime import date as date_type

    health_by_hours = 0.0
    health_by_age = 0.0
    remaining_hours = None
    remaining_days = None

    installed_runtime_hours = float(component.installed_runtime_hours or 0)
    used_runtime_hours = max(0, current_runtime_hours - installed_runtime_hours)

    # Life consumption by runtime hours
    if component.lifetime_hours and component.lifetime_hours > 0:
        usage_ratio = used_runtime_hours / component.lifetime_hours
        health_by_hours = min(usage_ratio * 100, 100)
        remaining_hours = max(0, component.lifetime_hours - used_runtime_hours)

    # Health by calendar age
    if component.lifetime_months and component.lifetime_months > 0:
        install_date = component.last_replacement_date or component.installation_date
        if install_date:
            today = date_type.today()
            months_elapsed = (today.year - install_date.year) * 12 + (today.month - install_date.month)
            age_ratio = months_elapsed / component.lifetime_months
            health_by_age = min(age_ratio * 100, 100)
            remaining_months = max(0, component.lifetime_months - months_elapsed)
            remaining_days = remaining_months * 30  # Approximate for planning horizon

    life_consumed_percent = max(health_by_hours, health_by_age)
    health_percent = max(0, 100 - life_consumed_percent)

    # Determine status
    critical_threshold = float(component.critical_threshold_percent) if component.critical_threshold_percent else 100
    warning_threshold = float(component.warning_threshold_percent) if component.warning_threshold_percent else 90

    if life_consumed_percent >= critical_threshold:
        health_status = "CRITICAL"
        maintenance_due_status = "EXPIRED" if life_consumed_percent >= 100 else "CRITICAL_DUE"
    elif life_consumed_percent >= warning_threshold:
        health_status = "WARNING"
        maintenance_due_status = "DUE_SOON"
    else:
        health_status = "HEALTHY"
        maintenance_due_status = "NOT_DUE"

    return {
        "component_id": component.component_id,
        "component_name": component.component_name,
        "component_type": component.component_type,
        "health_percent": round(health_percent, 2),
        "life_consumed_percent": round(life_consumed_percent, 2),
        "health_status": health_status,
        "maintenance_due_status": maintenance_due_status,
        "remaining_useful_life_hours": round(remaining_hours, 2) if remaining_hours is not None else None,
        "remaining_useful_life_days": round(remaining_days, 2) if remaining_days is not None else None,
        "current_runtime_hours": current_runtime_hours,
        "installed_runtime_hours": installed_runtime_hours,
        "used_runtime_hours": round(used_runtime_hours, 2),
        "lifetime_hours": component.lifetime_hours,
        "lifetime_months": component.lifetime_months,
        "installation_date": component.installation_date,
        "warning_threshold": warning_threshold,
        "critical_threshold": critical_threshold,
    }
