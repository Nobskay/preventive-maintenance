"""
Alert model - real-time maintenance alerts
"""
from sqlalchemy import Column, Integer, BigInteger, String, Text, Boolean, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Alert(BaseModel):
    __tablename__ = "alerts"

    alert_id = Column(BigInteger, primary_key=True, autoincrement=True)
    machine_id = Column(Integer, ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False, index=True)
    component_id = Column(Integer, ForeignKey("components.component_id", ondelete="SET NULL"), nullable=True)
    alert_type = Column(String(50), nullable=False)
    alert_severity = Column(String(50), default="warning")
    message = Column(Text, nullable=False)
    additional_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    machine = relationship("Machine", back_populates="alerts")
    component = relationship("Component", back_populates="alerts")

    def __repr__(self):
        return f"<Alert {self.alert_type} Machine#{self.machine_id}>"
