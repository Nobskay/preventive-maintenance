"""
Component model - replaceable/serviceable parts within machines
"""
from sqlalchemy import Column, Integer, String, Date, Text, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Component(BaseModel):
    __tablename__ = "components"

    component_id = Column(Integer, primary_key=True, autoincrement=True)
    machine_id = Column(Integer, ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False, index=True)
    component_name = Column(String(255), nullable=False)
    component_type = Column(String(100), nullable=False)
    lifetime_hours = Column(Integer, nullable=True)
    lifetime_months = Column(Integer, nullable=True)
    installed_runtime_hours = Column(Numeric(10, 2), default=0)
    warning_threshold_percent = Column(Numeric(5, 2), default=90)
    critical_threshold_percent = Column(Numeric(5, 2), default=100)
    replacement_cost = Column(Numeric(10, 2), nullable=True)
    maintenance_sop = Column(Text, nullable=True)
    installation_date = Column(Date, nullable=False)
    last_replacement_date = Column(Date, nullable=True)

    # Relationships
    machine = relationship("Machine", back_populates="components")
    alerts = relationship("Alert", back_populates="component")
    recommendations = relationship("MaintenanceRecommendation", back_populates="component")
    maintenance_events = relationship("MaintenanceEvent", back_populates="component")

    def __repr__(self):
        return f"<Component {self.component_name} on Machine#{self.machine_id}>"
