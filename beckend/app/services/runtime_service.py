"""
Runtime service - runtime tracking and CSV import
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from decimal import Decimal
import csv
import io

from app.models.runtime import Runtime
from app.schemas.runtime import RuntimeCreate


def get_runtime_records(
    db: Session,
    machine_id: int,
    skip: int = 0,
    limit: int = 100,
) -> List[Runtime]:
    return (
        db.query(Runtime)
        .filter(Runtime.machine_id == machine_id)
        .order_by(Runtime.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_latest_runtime(db: Session, machine_id: int) -> Optional[Runtime]:
    return (
        db.query(Runtime)
        .filter(Runtime.machine_id == machine_id)
        .order_by(Runtime.timestamp.desc())
        .first()
    )


def create_runtime_record(db: Session, data: RuntimeCreate) -> Runtime:
    latest = get_latest_runtime(db, data.machine_id)
    if latest and data.runtime_hours < latest.runtime_hours:
        raise ValueError("runtime_hours cannot be lower than the latest recorded runtime for this machine")

    # Calculate delta if not provided
    delta = data.delta_hours
    if delta is None:
        if latest:
            delta = data.runtime_hours - latest.runtime_hours
        else:
            delta = data.runtime_hours
    if delta < 0:
        raise ValueError("runtime_hours cannot be lower than the latest recorded runtime for this machine")

    record = Runtime(
        machine_id=data.machine_id,
        runtime_hours=data.runtime_hours,
        delta_hours=delta,
        timestamp=data.timestamp,
        data_source=data.data_source,
        notes=data.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def create_runtime_batch(db: Session, records: List[RuntimeCreate]) -> List[Runtime]:
    """Create multiple runtime records"""
    created = []
    for data in records:
        record = create_runtime_record(db, data)
        created.append(record)
    return created


def import_csv(db: Session, machine_id: int, file_content: str, data_source: str = "csv_import") -> dict:
    """Import runtime data from CSV"""
    reader = csv.DictReader(io.StringIO(file_content))
    imported = 0
    errors = []

    for i, row in enumerate(reader, 1):
        try:
            runtime_hours = Decimal(row["runtime_hours"])
            timestamp = datetime.fromisoformat(row.get("timestamp", datetime.utcnow().isoformat()))
            notes = row.get("notes", "")

            data = RuntimeCreate(
                machine_id=machine_id,
                runtime_hours=runtime_hours,
                timestamp=timestamp,
                data_source=data_source,
                notes=notes,
            )
            create_runtime_record(db, data)
            imported += 1
        except Exception as e:
            errors.append(f"Row {i}: {str(e)}")

    return {"imported": imported, "errors": errors}
