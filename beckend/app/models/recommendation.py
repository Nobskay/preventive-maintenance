"""
Maintenance Recommendation model - AI/rule-based maintenance suggestions
"""
from sqlalchemy import Column, Integer, BigInteger, String, Date, Text, Numeric, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class MaintenanceRecommendation(BaseModel):
    __tablename__ = "maintenance_recommendations"

    recommendation_id = Column(BigInteger, primary_key=True, autoincrement=True)
    machine_id = Column(Integer, ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False, index=True)
    component_id = Column(Integer, ForeignKey("components.component_id", ondelete="SET NULL"), nullable=True)
    recommendation_type = Column(String(100), nullable=False)
    recommended_by_system = Column(String(50), default="rule_engine")
    description = Column(Text, nullable=False)
    urgency = Column(String(50), default="medium")
    estimated_cost = Column(Numeric(10, 2), nullable=True)
    estimated_duration_hours = Column(Numeric(10, 2), nullable=True)
    status = Column(String(50), default="open")
    scheduled_date = Column(Date, nullable=True)
    completed_date = Column(Date, nullable=True)

    # Relationships
    machine = relationship("Machine", back_populates="recommendations")
    component = relationship("Component", back_populates="recommendations")

    def __repr__(self):
        return f"<Recommendation {self.recommendation_type} Machine#{self.machine_id}>"
