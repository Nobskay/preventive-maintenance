"""
Maintenance event model - completed inspections, repairs, PM tasks, and replacements.
"""
from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class MaintenanceEvent(BaseModel):
    __tablename__ = "maintenance_events"

    maintenance_event_id = Column(BigInteger, primary_key=True, autoincrement=True)
    machine_id = Column(Integer, ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False, index=True)
    component_id = Column(Integer, ForeignKey("components.component_id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = Column(String(50), nullable=False)
    trigger_source = Column(String(50), default="preventive")
    work_order_code = Column(String(100), nullable=True, unique=True)
    performed_at = Column(DateTime, nullable=False)
    duration_hours = Column(Numeric(10, 2), nullable=True)
    technician = Column(String(255), nullable=True)
    action_taken = Column(Text, nullable=False)
    parts_replaced = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)

    machine = relationship("Machine", back_populates="maintenance_events")
    component = relationship("Component", back_populates="maintenance_events")

    def __repr__(self):
        return f"<MaintenanceEvent {self.event_type} Machine#{self.machine_id}>"
