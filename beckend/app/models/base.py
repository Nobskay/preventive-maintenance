"""
Base ORM model with common fields
"""
from sqlalchemy import Column, DateTime, Integer, func
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

class BaseModel(Base):
    """
    Base model class with common fields for all ORM models
    """
    __abstract__ = True
    
    # Common timestamp fields
    created_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        server_default=func.now(),
    )
    updated_at = Column(
        DateTime,
        nullable=False,
        default=func.now(),
        onupdate=func.now(),
        server_default=func.now(),
    )
    
    def to_dict(self):
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
