"""
Maintenance event service - completed work history and PM traceability.
"""
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.maintenance import MaintenanceEvent
from app.schemas.maintenance import MaintenanceEventCreate, MaintenanceEventUpdate


def get_maintenance_events(
    db: Session,
    machine_id: Optional[int] = None,
    component_id: Optional[int] = None,
    event_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[MaintenanceEvent]:
    query = db.query(MaintenanceEvent)
    if machine_id:
        query = query.filter(MaintenanceEvent.machine_id == machine_id)
    if component_id:
        query = query.filter(MaintenanceEvent.component_id == component_id)
    if event_type:
        query = query.filter(MaintenanceEvent.event_type == event_type)
    return query.order_by(MaintenanceEvent.performed_at.desc()).offset(skip).limit(limit).all()


def get_maintenance_event(db: Session, maintenance_event_id: int) -> Optional[MaintenanceEvent]:
    return (
        db.query(MaintenanceEvent)
        .filter(MaintenanceEvent.maintenance_event_id == maintenance_event_id)
        .first()
    )


def create_maintenance_event(db: Session, data: MaintenanceEventCreate) -> MaintenanceEvent:
    event = MaintenanceEvent(**data.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


def update_maintenance_event(
    db: Session,
    maintenance_event_id: int,
    data: MaintenanceEventUpdate,
) -> Optional[MaintenanceEvent]:
    event = get_maintenance_event(db, maintenance_event_id)
    if not event:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(event, field, value)
    db.commit()
    db.refresh(event)
    return event


def delete_maintenance_event(db: Session, maintenance_event_id: int) -> bool:
    event = get_maintenance_event(db, maintenance_event_id)
    if not event:
        return False
    db.delete(event)
    db.commit()
    return True
