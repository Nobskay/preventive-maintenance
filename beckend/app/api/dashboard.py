"""
Dashboard API endpoints - KPIs and summary data
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas.common import ApiResponse
from app.services import kpi_service, machine_service, alert_service, recommendation_service

router = APIRouter()


@router.get("/summary", response_model=ApiResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    summary = kpi_service.get_dashboard_summary(db)
    return ApiResponse(data=summary)


@router.get("/kpis", response_model=ApiResponse)
def get_all_kpis(
    days: int = Query(90, ge=1, le=365),
    db: Session = Depends(get_db),
):
    kpis = kpi_service.calculate_all_machine_kpis(db, days=days)
    return ApiResponse(data=kpis)


@router.get("/kpis/{machine_id}", response_model=ApiResponse)
def get_machine_kpi(
    machine_id: int,
    days: int = Query(90, ge=1, le=365),
    db: Session = Depends(get_db),
):
    kpi = kpi_service.calculate_machine_kpi(db, machine_id, days=days)
    return ApiResponse(data=kpi)


@router.get("/machine-health", response_model=ApiResponse)
def get_all_machine_health(db: Session = Depends(get_db)):
    """Get health status for all machines"""
    from app.models.machine import Machine
    machines = db.query(Machine).all()
    health_data = []
    for machine in machines:
        health = machine_service.get_machine_health(db, machine.machine_id)
        if health:
            health_data.append(health)
    return ApiResponse(data=health_data)


@router.get("/downtime-trends", response_model=ApiResponse)
def get_downtime_trends(
    machine_id: Optional[int] = None,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    from app.services import downtime_service
    trends = downtime_service.get_downtime_trends(db, machine_id=machine_id, days=days)
    return ApiResponse(data=trends)


@router.get("/recommendations", response_model=ApiResponse)
def get_recommendations(
    machine_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    recs = recommendation_service.get_recommendations(db, machine_id=machine_id, status=status)
    from app.schemas.recommendation import RecommendationResponse
    return ApiResponse(data=[RecommendationResponse.model_validate(r) for r in recs])


@router.post("/generate-recommendations", response_model=ApiResponse)
def generate_recommendations(db: Session = Depends(get_db)):
    generated = recommendation_service.generate_recommendations(db)
    from app.schemas.recommendation import RecommendationResponse
    return ApiResponse(
        data=[RecommendationResponse.model_validate(r) for r in generated],
        message=f"Generated {len(generated)} recommendations",
    )
