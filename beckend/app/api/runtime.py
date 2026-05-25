"""
Runtime API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.schemas.runtime import RuntimeCreate, RuntimeResponse, RuntimeBatchCreate
from app.schemas.common import ApiResponse
from app.services import runtime_service

router = APIRouter()


@router.get("/{machine_id}", response_model=ApiResponse)
def list_runtime(
    machine_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
):
    records = runtime_service.get_runtime_records(db, machine_id, skip=skip, limit=limit)
    return ApiResponse(data=[RuntimeResponse.model_validate(r) for r in records])


@router.get("/{machine_id}/latest", response_model=ApiResponse)
def get_latest_runtime(machine_id: int, db: Session = Depends(get_db)):
    record = runtime_service.get_latest_runtime(db, machine_id)
    if not record:
        raise HTTPException(status_code=404, detail="No runtime data found")
    return ApiResponse(data=RuntimeResponse.model_validate(record))


@router.post("/", response_model=ApiResponse, status_code=201)
def create_runtime(data: RuntimeCreate, db: Session = Depends(get_db)):
    try:
        record = runtime_service.create_runtime_record(db, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ApiResponse(data=RuntimeResponse.model_validate(record), message="Runtime record created")


@router.post("/batch", response_model=ApiResponse, status_code=201)
def create_runtime_batch(data: RuntimeBatchCreate, db: Session = Depends(get_db)):
    try:
        records = runtime_service.create_runtime_batch(db, data.records)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return ApiResponse(
        data=[RuntimeResponse.model_validate(r) for r in records],
        message=f"{len(records)} runtime records created",
    )


@router.post("/{machine_id}/import-csv", response_model=ApiResponse)
async def import_csv(machine_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    result = runtime_service.import_csv(db, machine_id, content.decode("utf-8"))
    return ApiResponse(data=result, message=f"Imported {result['imported']} records")
