"""
Machine model - core equipment in the facility
"""
from sqlalchemy import Column, Integer, String, Date, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Machine(BaseModel):
    __tablename__ = "machines"

    machine_id = Column(Integer, primary_key=True, autoincrement=True)
    machine_name = Column(String(255), nullable=False)
    machine_type = Column(String(100), nullable=False)
    manufacturer = Column(String(255))
    installation_date = Column(Date, nullable=False)
    operating_schedule = Column(String(50), default="continuous")
    status = Column(String(50), default="active")
    notes = Column(Text, nullable=True)

    # Relationships
    components = relationship("Component", back_populates="machine", cascade="all, delete-orphan")
    runtime_records = relationship("Runtime", back_populates="machine", cascade="all, delete-orphan")
    downtime_records = relationship("Downtime", back_populates="machine", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="machine", cascade="all, delete-orphan")
    recommendations = relationship("MaintenanceRecommendation", back_populates="machine", cascade="all, delete-orphan")
    maintenance_events = relationship("MaintenanceEvent", back_populates="machine", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Machine {self.machine_name} ({self.machine_type})>"
