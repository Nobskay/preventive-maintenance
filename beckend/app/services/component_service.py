"""
Component service - CRUD operations and health calculations
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date

from app.models.component import Component
from app.models.runtime import Runtime
from app.schemas.component import ComponentCreate, ComponentUpdate


def _validate_component_lifecycle(component: Component) -> None:
    if component.lifetime_hours is None and component.lifetime_months is None:
        raise ValueError("At least one lifecycle limit is required: lifetime_hours or lifetime_months")
    if component.warning_threshold_percent is None or component.critical_threshold_percent is None:
        raise ValueError("warning and critical threshold percentages are required")
    if component.warning_threshold_percent >= component.critical_threshold_percent:
        raise ValueError("warning_threshold_percent must be lower than critical_threshold_percent")


def get_components(
    db: Session,
    machine_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[Component]:
    query = db.query(Component)
    if machine_id:
        query = query.filter(Component.machine_id == machine_id)
    return query.order_by(Component.component_name).offset(skip).limit(limit).all()


def get_component(db: Session, component_id: int) -> Optional[Component]:
    return db.query(Component).filter(Component.component_id == component_id).first()


def create_component(db: Session, data: ComponentCreate) -> Component:
    component = Component(**data.model_dump())
    _validate_component_lifecycle(component)
    db.add(component)
    db.commit()
    db.refresh(component)
    return component


def update_component(db: Session, component_id: int, data: ComponentUpdate) -> Optional[Component]:
    component = get_component(db, component_id)
    if not component:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(component, field, value)
    _validate_component_lifecycle(component)
    db.commit()
    db.refresh(component)
    return component


def delete_component(db: Session, component_id: int) -> bool:
    component = get_component(db, component_id)
    if not component:
        return False
    db.delete(component)
    db.commit()
    return True


def get_component_count(db: Session, machine_id: Optional[int] = None) -> int:
    query = db.query(func.count(Component.component_id))
    if machine_id:
        query = query.filter(Component.machine_id == machine_id)
    return query.scalar()


def get_component_health(db: Session, component_id: int) -> Optional[dict]:
    """Get health data for a single component"""
    component = get_component(db, component_id)
    if not component:
        return None

    # Get latest runtime
    latest_runtime = (
        db.query(Runtime)
        .filter(Runtime.machine_id == component.machine_id)
        .order_by(Runtime.timestamp.desc())
        .first()
    )
    current_hours = float(latest_runtime.runtime_hours) if latest_runtime else 0

    from app.services.machine_service import _calculate_component_health
    return _calculate_component_health(component, current_hours, db)
