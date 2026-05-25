"""
Recommendation service - maintenance recommendation generation
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.models.recommendation import MaintenanceRecommendation
from app.models.component import Component
from app.models.runtime import Runtime
from app.schemas.recommendation import RecommendationCreate, RecommendationUpdate


def get_recommendations(
    db: Session,
    machine_id: Optional[int] = None,
    status: Optional[str] = None,
    urgency: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> List[MaintenanceRecommendation]:
    query = db.query(MaintenanceRecommendation)
    if machine_id:
        query = query.filter(MaintenanceRecommendation.machine_id == machine_id)
    if status:
        query = query.filter(MaintenanceRecommendation.status == status)
    if urgency:
        query = query.filter(MaintenanceRecommendation.urgency == urgency)
    return query.order_by(MaintenanceRecommendation.created_at.desc()).offset(skip).limit(limit).all()


def get_recommendation(db: Session, recommendation_id: int) -> Optional[MaintenanceRecommendation]:
    return db.query(MaintenanceRecommendation).filter(MaintenanceRecommendation.recommendation_id == recommendation_id).first()


def create_recommendation(db: Session, data: RecommendationCreate) -> MaintenanceRecommendation:
    rec = MaintenanceRecommendation(**data.model_dump(), recommended_by_system="rule_engine")
    db.add(rec)
    db.commit()
    db.refresh(rec)
    return rec


def update_recommendation(db: Session, recommendation_id: int, data: RecommendationUpdate) -> Optional[MaintenanceRecommendation]:
    rec = get_recommendation(db, recommendation_id)
    if not rec:
        return None
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(rec, field, value)
    if data.status == "completed":
        rec.completed_date = datetime.utcnow().date()
    db.commit()
    db.refresh(rec)
    return rec


def generate_recommendations(db: Session) -> List[MaintenanceRecommendation]:
    """Generate maintenance recommendations based on component health"""
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

        # Skip if already has open recommendation
        existing = (
            db.query(MaintenanceRecommendation)
            .filter(
                MaintenanceRecommendation.component_id == comp.component_id,
                MaintenanceRecommendation.status.in_(["open", "scheduled"]),
            )
            .first()
        )
        if existing:
            continue

        if health["health_status"] == "CRITICAL":
            rec = create_recommendation(
                db,
                RecommendationCreate(
                    machine_id=comp.machine_id,
                    component_id=comp.component_id,
                    recommendation_type="replacement",
                    description=f"Replace {comp.component_name} - life consumed at {health['life_consumed_percent']}%. Remaining useful life: {health['remaining_useful_life_hours']}h",
                    urgency="immediate",
                    estimated_cost=comp.replacement_cost,
                    estimated_duration_hours=4,
                ),
            )
            generated.append(rec)

        elif health["health_status"] == "WARNING":
            rec = create_recommendation(
                db,
                RecommendationCreate(
                    machine_id=comp.machine_id,
                    component_id=comp.component_id,
                    recommendation_type="inspection",
                    description=f"Inspect {comp.component_name} - life consumed at {health['life_consumed_percent']}%. Plan replacement within {health['remaining_useful_life_days']} days.",
                    urgency="high",
                    estimated_cost=comp.replacement_cost,
                    estimated_duration_hours=2,
                ),
            )
            generated.append(rec)

    return generated
