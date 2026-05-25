"""
Downtime API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas.downtime import DowntimeCreate, DowntimeUpdate, DowntimeResponse
from app.schemas.common import ApiResponse
from app.services import downtime_service

router = APIRouter()


@router.get("/trends/", response_model=ApiResponse)
def get_downtime_trends(
    machine_id: Optional[int] = None,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    trends = downtime_service.get_downtime_trends(db, machine_id=machine_id, days=days)
    return ApiResponse(data=trends)


@router.get("/", response_model=ApiResponse)
def list_downtime(
    machine_id: Optional[int] = None,
    severity: Optional[str] = None,
    unplanned_only: bool = False,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    records = downtime_service.get_downtime_records(
        db, machine_id=machine_id, severity=severity, unplanned_only=unplanned_only, skip=skip, limit=limit
    )
    return ApiResponse(data=[DowntimeResponse.model_validate(r) for r in records])


@router.get("/{downtime_id}", response_model=ApiResponse)
def get_downtime(downtime_id: int, db: Session = Depends(get_db)):
    record = downtime_service.get_downtime(db, downtime_id)
    if not record:
        raise HTTPException(status_code=404, detail="Downtime record not found")
    return ApiResponse(data=DowntimeResponse.model_validate(record))


@router.post("/", response_model=ApiResponse, status_code=201)
def create_downtime(data: DowntimeCreate, db: Session = Depends(get_db)):
    try:
        record = downtime_service.create_downtime(db, data)
        return ApiResponse(data=DowntimeResponse.model_validate(record), message="Downtime record created")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{downtime_id}", response_model=ApiResponse)
def update_downtime(downtime_id: int, data: DowntimeUpdate, db: Session = Depends(get_db)):
    try:
        record = downtime_service.update_downtime(db, downtime_id, data)
    if not record:
        raise HTTPException(status_code=404, detail="Downtime record not found")
    return ApiResponse(data=DowntimeResponse.model_validate(record), message="Downtime record updated")


@router.delete("/{downtime_id}", response_model=ApiResponse)
def delete_downtime(downtime_id: int, db: Session = Depends(get_db)):
    success = downtime_service.delete_downtime(db, downtime_id)
    if not success:
        raise HTTPException(status_code=404, detail="Downtime record not found")
    return ApiResponse(message="Downtime record deleted")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
