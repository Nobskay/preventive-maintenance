"""
Machine API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas.machine import MachineCreate, MachineUpdate, MachineResponse, MachineWithHealth
from app.schemas.common import ApiResponse
from app.services import machine_service

router = APIRouter()


@router.get("/", response_model=ApiResponse)
def list_machines(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    status: Optional[str] = None,
    machine_type: Optional[str] = None,
    db: Session = Depends(get_db),
):
    machines = machine_service.get_machines(db, skip=skip, limit=limit, status=status, machine_type=machine_type)
    return ApiResponse(data=[MachineResponse.model_validate(m) for m in machines])


@router.get("/{machine_id}", response_model=ApiResponse)
def get_machine(machine_id: int, db: Session = Depends(get_db)):
    machine = machine_service.get_machine(db, machine_id)
    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found")
    return ApiResponse(data=MachineResponse.model_validate(machine))


@router.post("/", response_model=ApiResponse, status_code=201)
def create_machine(data: MachineCreate, db: Session = Depends(get_db)):
    try:
        machine = machine_service.create_machine(db, data)
        return ApiResponse(data=MachineResponse.model_validate(machine), message="Machine created successfully")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{machine_id}", response_model=ApiResponse)
def update_machine(machine_id: int, data: MachineUpdate, db: Session = Depends(get_db)):
    try:
        machine = machine_service.update_machine(db, machine_id, data)
        if not machine:
            raise HTTPException(status_code=404, detail="Machine not found")
        return ApiResponse(data=MachineResponse.model_validate(machine), message="Machine updated successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{machine_id}", response_model=ApiResponse)
def delete_machine(machine_id: int, db: Session = Depends(get_db)):
    success = machine_service.delete_machine(db, machine_id)
    if not success:
        raise HTTPException(status_code=404, detail="Machine not found")
    return ApiResponse(message="Machine deleted successfully")


@router.get("/{machine_id}/health", response_model=ApiResponse)
def get_machine_health(machine_id: int, db: Session = Depends(get_db)):
    health = machine_service.get_machine_health(db, machine_id)
    if not health:
        raise HTTPException(status_code=404, detail="Machine not found")
    return ApiResponse(data=health)
