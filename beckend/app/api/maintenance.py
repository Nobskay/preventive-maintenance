"""
Maintenance event API endpoints.
"""
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.common import ApiResponse
from app.schemas.maintenance import (
    MaintenanceEventCreate,
    MaintenanceEventUpdate,
    MaintenanceEventResponse,
)
from app.services import maintenance_service

router = APIRouter()


@router.get("/", response_model=ApiResponse)
def list_maintenance_events(
    machine_id: Optional[int] = None,
    component_id: Optional[int] = None,
    event_type: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    events = maintenance_service.get_maintenance_events(
        db,
        machine_id=machine_id,
        component_id=component_id,
        event_type=event_type,
        skip=skip,
        limit=limit,
    )
    return ApiResponse(data=[MaintenanceEventResponse.model_validate(event) for event in events])


@router.get("/{maintenance_event_id}", response_model=ApiResponse)
def get_maintenance_event(maintenance_event_id: int, db: Session = Depends(get_db)):
    event = maintenance_service.get_maintenance_event(db, maintenance_event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Maintenance event not found")
    return ApiResponse(data=MaintenanceEventResponse.model_validate(event))


@router.post("/", response_model=ApiResponse, status_code=201)
def create_maintenance_event(data: MaintenanceEventCreate, db: Session = Depends(get_db)):
    event = maintenance_service.create_maintenance_event(db, data)
    return ApiResponse(
        data=MaintenanceEventResponse.model_validate(event),
        message="Maintenance event created",
    )


@router.put("/{maintenance_event_id}", response_model=ApiResponse)
def update_maintenance_event(
    maintenance_event_id: int,
    data: MaintenanceEventUpdate,
    db: Session = Depends(get_db),
):
    event = maintenance_service.update_maintenance_event(db, maintenance_event_id, data)
    if not event:
        raise HTTPException(status_code=404, detail="Maintenance event not found")
    return ApiResponse(
        data=MaintenanceEventResponse.model_validate(event),
        message="Maintenance event updated",
    )


@router.delete("/{maintenance_event_id}", response_model=ApiResponse)
def delete_maintenance_event(maintenance_event_id: int, db: Session = Depends(get_db)):
    success = maintenance_service.delete_maintenance_event(db, maintenance_event_id)
    if not success:
        raise HTTPException(status_code=404, detail="Maintenance event not found")
    return ApiResponse(message="Maintenance event deleted")
