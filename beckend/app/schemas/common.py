"""
Common response schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Any, List, Generic, TypeVar
from datetime import datetime

T = TypeVar("T")


class ApiResponse(BaseModel, Generic[T]):
    success: bool = True
    data: Optional[T] = None
    message: str = "Success"
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    limit: int
    total_pages: int


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
