"""
Component API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas.component import ComponentCreate, ComponentUpdate, ComponentResponse, ComponentHealth
from app.schemas.common import ApiResponse
from app.services import component_service

router = APIRouter()


@router.get("/", response_model=ApiResponse)
def list_components(
    machine_id: Optional[int] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    components = component_service.get_components(db, machine_id=machine_id, skip=skip, limit=limit)
    return ApiResponse(data=[ComponentResponse.model_validate(c) for c in components])


@router.get("/{component_id}", response_model=ApiResponse)
def get_component(component_id: int, db: Session = Depends(get_db)):
    component = component_service.get_component(db, component_id)
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    return ApiResponse(data=ComponentResponse.model_validate(component))


@router.post("/", response_model=ApiResponse, status_code=201)
def create_component(data: ComponentCreate, db: Session = Depends(get_db)):
    try:
        component = component_service.create_component(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ApiResponse(data=ComponentResponse.model_validate(component), message="Component created successfully")


@router.put("/{component_id}", response_model=ApiResponse)
def update_component(component_id: int, data: ComponentUpdate, db: Session = Depends(get_db)):
    try:
        component = component_service.update_component(db, component_id, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not component:
        raise HTTPException(status_code=404, detail="Component not found")
    return ApiResponse(data=ComponentResponse.model_validate(component), message="Component updated successfully")


@router.delete("/{component_id}", response_model=ApiResponse)
def delete_component(component_id: int, db: Session = Depends(get_db)):
    success = component_service.delete_component(db, component_id)
    if not success:
        raise HTTPException(status_code=404, detail="Component not found")
    return ApiResponse(message="Component deleted successfully")


@router.get("/{component_id}/health", response_model=ApiResponse)
def get_component_health(component_id: int, db: Session = Depends(get_db)):
    health = component_service.get_component_health(db, component_id)
    if not health:
        raise HTTPException(status_code=404, detail="Component not found")
    return ApiResponse(data=health)
