"""
Alert API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas.alert import AlertCreate, AlertResolve, AlertResponse
from app.schemas.common import ApiResponse
from app.services import alert_service

router = APIRouter()


@router.post("/generate", response_model=ApiResponse)
def generate_alerts(db: Session = Depends(get_db)):
    """Scan components and generate maintenance alerts"""
    generated = alert_service.generate_maintenance_alerts(db)
    return ApiResponse(
        data=[AlertResponse.model_validate(a) for a in generated],
        message=f"Generated {len(generated)} alerts",
    )


@router.get("/", response_model=ApiResponse)
def list_alerts(
    machine_id: Optional[int] = None,
    active_only: bool = False,
    severity: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    alerts = alert_service.get_alerts(
        db, machine_id=machine_id, active_only=active_only, severity=severity, skip=skip, limit=limit
    )
    return ApiResponse(data=[AlertResponse.model_validate(a) for a in alerts])


@router.get("/{alert_id}", response_model=ApiResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    alert = alert_service.get_alert(db, alert_id)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return ApiResponse(data=AlertResponse.model_validate(alert))


@router.post("/", response_model=ApiResponse, status_code=201)
def create_alert(data: AlertCreate, db: Session = Depends(get_db)):
    alert = alert_service.create_alert(db, data)
    return ApiResponse(data=AlertResponse.model_validate(alert), message="Alert created")


@router.post("/{alert_id}/resolve", response_model=ApiResponse)
def resolve_alert(alert_id: int, data: AlertResolve, db: Session = Depends(get_db)):
    alert = alert_service.resolve_alert(db, alert_id, data)
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    return ApiResponse(data=AlertResponse.model_validate(alert), message="Alert resolved")
