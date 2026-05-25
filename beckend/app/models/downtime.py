"""
Downtime model - maintenance and unplanned downtime events
"""
from sqlalchemy import Column, Integer, BigInteger, String, Text, Boolean, DateTime, ForeignKey, Interval
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Downtime(BaseModel):
    __tablename__ = "downtime"

    downtime_id = Column(BigInteger, primary_key=True, autoincrement=True)
    machine_id = Column(Integer, ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp_start = Column(DateTime, nullable=False)
    timestamp_end = Column(DateTime, nullable=False)
    downtime_duration = Column(Interval, nullable=True)
    issue_description = Column(Text, nullable=False)
    root_cause = Column(Text, nullable=True)
    corrective_action = Column(Text, nullable=True)
    severity_level = Column(String(50), nullable=False, default="medium")
    component_affected = Column(Integer, ForeignKey("components.component_id"), nullable=True)
    reported_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    resolved_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    is_unplanned = Column(Boolean, default=True)

    # Relationships
    machine = relationship("Machine", back_populates="downtime_records")
    affected_component = relationship("Component", foreign_keys=[component_affected])

    def __repr__(self):
        return f"<Downtime Machine#{self.machine_id} {self.severity_level}>"
