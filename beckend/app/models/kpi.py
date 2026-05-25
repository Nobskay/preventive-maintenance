"""
KPI Snapshot model - historical KPI data for trend analysis
"""
from sqlalchemy import Column, Integer, BigInteger, String, Date, Numeric, DateTime, ForeignKey
from app.models.base import BaseModel


class KPISnapshot(BaseModel):
    __tablename__ = "kpi_snapshots"

    snapshot_id = Column(BigInteger, primary_key=True, autoincrement=True)
    machine_id = Column(Integer, ForeignKey("machines.machine_id", ondelete="CASCADE"), nullable=False, index=True)
    mtbf_hours = Column(Numeric(10, 2), nullable=True)
    mttr_hours = Column(Numeric(10, 2), nullable=True)
    availability_percent = Column(Numeric(5, 2), nullable=True)
    failure_frequency = Column(Numeric(10, 4), nullable=True)
    total_uptime_hours = Column(Numeric(10, 2), nullable=True)
    total_downtime_hours = Column(Numeric(10, 2), nullable=True)
    total_failures = Column(Integer, nullable=True)
    snapshot_date = Column(Date, nullable=False)
    time_period = Column(String(50), default="month")

    def __repr__(self):
        return f"<KPISnapshot Machine#{self.machine_id} {self.snapshot_date}>"
