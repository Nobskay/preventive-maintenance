"""
Downtime service - downtime logging and analysis
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.models.downtime import Downtime
from app.schemas.downtime import DowntimeCreate, DowntimeUpdate


def get_downtime_records(
    db: Session,
    machine_id: Optional[int] = None,
    severity: Optional[str] = None,
    unplanned_only: bool = False,
    skip: int = 0,
    limit: int = 100,
) -> List[Downtime]:
    query = db.query(Downtime)
    if machine_id:
        query = query.filter(Downtime.machine_id == machine_id)
    if severity:
        query = query.filter(Downtime.severity_level == severity)
    if unplanned_only:
        query = query.filter(Downtime.is_unplanned == True)
    return query.order_by(Downtime.timestamp_start.desc()).offset(skip).limit(limit).all()


def get_downtime(db: Session, downtime_id: int) -> Optional[Downtime]:
    return db.query(Downtime).filter(Downtime.downtime_id == downtime_id).first()


def create_downtime(db: Session, data: DowntimeCreate) -> Downtime:
    duration = data.timestamp_end - data.timestamp_start
    record = Downtime(
        machine_id=data.machine_id,
        timestamp_start=data.timestamp_start,
        timestamp_end=data.timestamp_end,
        downtime_duration=duration,
        issue_description=data.issue_description,
        root_cause=data.root_cause,
        corrective_action=data.corrective_action,
        severity_level=data.severity_level,
        component_affected=data.component_affected,
        is_unplanned=data.is_unplanned,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def update_downtime(db: Session, downtime_id: int, data: DowntimeUpdate) -> Optional[Downtime]:
    record = get_downtime(db, downtime_id)
    if not record:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(record, field, value)
    # Recalculate duration if timestamps changed
    if record.timestamp_start and record.timestamp_end:
        if record.timestamp_start >= record.timestamp_end:
            raise ValueError("timestamp_start must be before timestamp_end")
        record.downtime_duration = record.timestamp_end - record.timestamp_start
    db.commit()
    db.refresh(record)
    return record


def delete_downtime(db: Session, downtime_id: int) -> bool:
    record = get_downtime(db, downtime_id)
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True


def get_downtime_trends(db: Session, machine_id: Optional[int] = None, days: int = 30) -> List[dict]:
    """Get downtime trends for the last N days"""
    cutoff = datetime.utcnow() - timedelta(days=days)
    query = db.query(Downtime).filter(Downtime.timestamp_start >= cutoff)
    if machine_id:
        query = query.filter(Downtime.machine_id == machine_id)

    buckets: dict[str, dict] = {}
    for event in query.order_by(Downtime.timestamp_start.asc()).all():
        bucket_date = event.timestamp_start.date().isoformat()
        duration = event.downtime_duration or (event.timestamp_end - event.timestamp_start)
        hours = duration.total_seconds() / 3600 if duration else 0
        bucket = buckets.setdefault(
            bucket_date,
            {
                "date": bucket_date,
                "total_downtime_hours": 0.0,
                "unplanned_downtime_hours": 0.0,
                "failure_count": 0,
            },
        )
        bucket["total_downtime_hours"] += hours
        if event.is_unplanned:
            bucket["unplanned_downtime_hours"] += hours
            bucket["failure_count"] += 1

    return [
        {
            **bucket,
            "total_downtime_hours": round(bucket["total_downtime_hours"], 2),
            "unplanned_downtime_hours": round(bucket["unplanned_downtime_hours"], 2),
        }
        for bucket in buckets.values()
    ]
