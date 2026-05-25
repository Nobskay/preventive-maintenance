"""
Runtime model - time-series operational hours tracking
"""
from sqlalchemy import Column, Integer, BigInteger, String, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Runtime(BaseModel):
    __tablename__ = "runtime"

    runtime_id = Column(BigInteger, primary_key=True, autoincrement=True)
    machine_id = Column(Integer, ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False, index=True)
    runtime_hours = Column(Numeric(10, 2), nullable=False)
    delta_hours = Column(Numeric(10, 2), nullable=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    data_source = Column(String(50), default="manual")
    recorded_by = Column(Integer, ForeignKey("users.user_id"), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    machine = relationship("Machine", back_populates="runtime_records")

    def __repr__(self):
        return f"<Runtime Machine#{self.machine_id} {self.runtime_hours}h @ {self.timestamp}>"
