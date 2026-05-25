"""
Runtime schemas for request/response validation
"""
from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal


class DataSource(str, Enum):
    MANUAL = "manual"
    CSV_IMPORT = "csv_import"
    IOT = "iot"
    PLC = "plc"
    API = "api"
    SCADA = "scada"


class RuntimeBase(BaseModel):
    machine_id: int
    runtime_hours: Decimal = Field(..., ge=0)
    delta_hours: Optional[Decimal] = Field(None, ge=0)
    timestamp: datetime
    data_source: DataSource = DataSource.MANUAL
    notes: Optional[str] = None


class RuntimeCreate(RuntimeBase):
    pass


class RuntimeBatchCreate(BaseModel):
    records: List[RuntimeCreate]


class RuntimeResponse(RuntimeBase):
    runtime_id: int

    class Config:
        from_attributes = True


class RuntimeCSVImport(BaseModel):
    machine_id: int
    file_content: str
    data_source: DataSource = DataSource.CSV_IMPORT
